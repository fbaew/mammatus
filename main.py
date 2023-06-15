from multiprocessing import Process, Queue
import argparse
import sqlite3
import datetime
import os
import time
import requests
from PIL import Image, ImageSequence
import imageio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class RadarFetcher:
    def __init__(self, city, zoom=0, frames=10, output=None, db_queue=None):
        self.city = city
        self.zoom = zoom
        self.frames = frames
        self.images = []
        self.output = output or f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{self.city}_z{self.zoom}.gif"
        self.db_queue = db_queue

    def get_coordinates(self):
        url = f"https://nominatim.openstreetmap.org/search/{self.city}?format=json&addressdetails=0&limit=1"

        response = requests.get(url)
        data = response.json()

        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return float(lat), float(lon)
        else:
            return None, None

    def capture_radar(self, force_write=False):
        coords = self.get_coordinates()
        lat, lng = coords 
        url = f'https://www.theweathernetwork.com/en/maps/radar?lat={lat}&lng={lng}'
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M")

        # setup webdriver
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--log-level=3")  # This will suppress all messages except fatal errors

        service = Service(r'chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)

        try:
            print('Loading weather radar...')
            # Navigate to the webpage
            driver.get(url)

            # Wait for page to load
            time.sleep(5)  # Adjust this delay as needed

        except:

            pass

        # Close cookie bar if it is present
        try:
            print('Dismissing cookie banner')
            cookie_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="cookie-bar-close-button"]')))
            cookie_button.click()
        except:
            pass

        # Hide unwanted elements
        elements_to_hide = ['responsive-header-bar', 'div-gpt-ad-topbanner-short']
        for element in elements_to_hide:
            try:
                print(f'Hiding unwanted elements')
                unwanted_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-testid="{element}"]')))
                driver.execute_script("arguments[0].style.visibility='hidden'", unwanted_element)
                print('Done ')
            except:
                pass

        # Toggle fullscreen
        try:
            full_screen_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Toggle Full Screen"]')))
            full_screen_button.click()
        except:
            pass

        # Zoom in or out
        if self.zoom > 0:
            try:
                zoom_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Zoom In"]')))
                for _ in range(self.zoom):
                    zoom_button.click()
                    time.sleep(1)  # add delay between each click
            except:
                pass
        elif self.zoom < 0:
            try:
                zoom_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Zoom Out"]')))
                for _ in range(abs(self.zoom)):
                    zoom_button.click()
                    time.sleep(1)  # add delay between each click
            except:
                pass

        # Wait for the play/pause button to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="play-pause-button"]')))

        # Click the play button
        play_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="play-pause-button"]')
        play_button.click()

        # Take screenshots every 1 second for the duration
        for idx, _ in enumerate(range(self.frames)):
            print(f'Collecting screenshot {idx+1}/{self.frames}')
            image = driver.get_screenshot_as_png()
            self.images.append(imageio.imread(image))
#            time.sleep(1)

        # Close the browser
        driver.quit()

        # Add data to the database queue
        if self.db_queue is not None:
            self.db_queue.put((self.city, self.zoom, timestamp, self.output))

        if force_write:
            print('Forcing GIF write')
            self.write_gif()

    def write_gif(self):
        # Create the output directory if it doesn't exist
        os.makedirs('outputs', exist_ok=True)

        # Add the directory to the filename
        output_filename = os.path.join('outputs', self.output)

        imageio.mimsave(output_filename, self.images)

        # Create a scaled-down version of the GIF
        self.write_small_gif(output_filename)

    def write_small_gif(self, filename):
        # Load the original GIF
        with Image.open(filename) as im:
            size = im.size
            duration = im.info['duration']
            frames = [frame.copy() for frame in ImageSequence.Iterator(im)]

        # Scale down the GIF
        scale = 0.1
        new_size = (int(size[0] * scale), int(size[1] * scale))
        new_frames = [frame.resize(new_size) for frame in frames]

        # Save the scaled-down GIF
        new_filename = os.path.splitext(filename)[0] + '_scaled.gif'
        new_frames[0].save(new_filename, save_all=True, append_images=new_frames[1:], duration=duration, loop=0)


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.queue = Queue()

    def start(self):
        self.process = Process(target=self.run)
        self.process.start()

    def stop(self):
        self.queue.put(None)
        self.process.join()

    def run(self):
        conn = sqlite3.connect(self.db_path)

        while True:
            data = self.queue.get()
            if data is None:
                break

            city, zoom, timestamp, filename = data

            # Insert the new image into the table
            conn.execute('INSERT INTO radar_images (city, zoom, filename) VALUES (?, ?, ?)', (city, zoom, filename))
            # Delete the oldest image if there are more than 5 for this location+zoom combination
            conn.execute('DELETE FROM radar_images WHERE id IN (SELECT id FROM radar_images WHERE city = ? AND zoom = ? ORDER BY created_at ASC LIMIT -1 OFFSET 5)', (city, zoom))

            # Commit the changes
            conn.commit()

        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture weather radar images and assemble them into a gif.')
    parser.add_argument('city', type=str, help='The city to capture the radar images of.')
    parser.add_argument('-f', '--frames', type=int, default=10, help='The number of frames to capture for the radar animation.')
    parser.add_argument('-z', '--zoom', type=int, default=0, help='The zoom level for radar images. Can be 0, 1, 2, 3, or 4.')
    parser.add_argument('-o', '--output', type=str, default=None, help='The filename to save the output gif to. If not specified, a filename will be generated based on the current time, city, and zoom level.')
    parser.add_argument('-d', '--db-path', type=str, default='radar_images.db', help='The path to the SQLite database file to use for storing radar images.')

    args = parser.parse_args()

    db_manager = DatabaseManager(args.db_path)
    db_manager.start()

    fetcher = RadarFetcher(args.city, zoom=args.zoom, frames=args.frames, output=args.output, db_queue=db_manager.queue)
    fetcher.capture_radar()
    fetcher.write_gif()

    db_manager.stop()
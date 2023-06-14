from PIL import Image, ImageSequence
import argparse
import sqlite3
import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


import imageio

import requests


class RadarFetcher:
    def __init__(self, city, zoom=0, frames=10, output=None):
        self.city = city
        self.zoom = zoom
        self.frames = frames
        self.images = []
        self.output = output

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

    def capture_radar(self):
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

    def write_gif(self):
        if self.output is None:
            coords = self.get_coordinates()
            lat, lng = coords 
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d%H%M")
            filename = f"{timestamp}_{self.city}_z{self.zoom}.gif"
        else:
            filename = self.output

        # Create the output directory if it doesn't exist
        os.makedirs('outputs', exist_ok=True)

        # Add the directory to the filename
        output_filename = os.path.join('outputs', filename)

        # Connect to the database
        conn = sqlite3.connect('radar_images.db')

        # Insert the new image into the table
        conn.execute('INSERT INTO radar_images (city, zoom, filename) VALUES (?, ?, ?)', (self.city, self.zoom, filename))
        # Delete the oldest image if there are more than 5 for this location+zoom combination
        conn.execute('DELETE FROM radar_images WHERE id IN (SELECT id FROM radar_images WHERE city = ? AND zoom = ? ORDER BY created_at ASC LIMIT -1 OFFSET 5)', (self.city, self.zoom))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture weather radar images and assemble them into a gif.')
    parser.add_argument('city', type=str, help='The city to capture the radar images of.')
    parser.add_argument('-f', '--frames', type=int, default=10, help='The number of frames to capture for the radar animation.')
    parser.add_argument('-z', '--zoom', type=int, default=0, help='The zoom level for radar images. Can be 0, 1, 2, 3, or 4.')
    parser.add_argument('-o', '--output', type=str, default=None, help='The filename to save the output gif to. If not specified, a filename will be generated based on the current time, city, and zoom level.')

    args = parser.parse_args()

    fetcher = RadarFetcher(args.city, zoom=args.zoom, frames=args.frames, output=args.output)
    fetcher.capture_radar()
    fetcher.write_gif()
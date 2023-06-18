from weather_providers import WeatherNetwork, Windy

import argparse
import sqlite3
import datetime
import os
import time
import requests
import imageio

from multiprocessing import Process, Queue
from PIL import Image, ImageSequence
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class RadarFetcher:
    def __init__(self, city, zoom=0, frames=10, output=None, db_queue=None, source='weathernetwork', mode=None, debug=False):
        self.city = city
        self.zoom = zoom
        self.frames = frames
        self.images = []
        self.output = output or f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{self.city}_z{self.zoom}.gif"
        self.db_queue = db_queue
        self.source = source
        self.mode = mode
        self.debug = debug

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
        if self.source == 'weathernetwork':
            url = f'https://www.theweathernetwork.com/en/maps/radar?lat={lat}&lng={lng}'
        elif self.source == 'windy':
            url = f'https://www.windy.com/?{lat},{lng}'
        elif self.source == 'acuweather':
            # This is fake. I haven't actually implemented anything for this one.
            url = f'https://www.accuweather.com/en/ca/toronto/m5j/weather-radar/55488_pc'

        # setup webdriver
        options = Options()
        if not self.debug:
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

        weather_provider = None
        if self.source == 'weathernetwork':
            weather_provider = WeatherNetwork(driver)
        elif self.source == 'windy':
            weather_provider = Windy(driver, zoom=self.zoom, mode=self.mode)

        weather_provider.prep()
        weather_provider.animate()

        # Take screenshots every 1 second for the duration
        for idx, _ in enumerate(range(self.frames)):
            print(f'Collecting screenshot {idx+1}/{self.frames}')
            image = weather_provider.capture_frame()
            self.images.append(image)

        # Close the browser
        driver.quit()

        # Add data to the database queue
        if self.db_queue is not None:
            self.db_queue.put((self.city, self.zoom, self.source, self.mode, self.output))

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

            city, zoom, source, mode, filename = data

            # Insert the new image into the table
            source_string = f'{source}_{mode}' if mode else source
            conn.execute('INSERT INTO radar_images (city, zoom, source, filename) VALUES (?, ?, ?, ?)', (city, zoom, source_string, filename))
            # Delete the oldest image if there are more than 5 for this location+zoom combination
            conn.execute('DELETE FROM radar_images WHERE id IN (SELECT id FROM radar_images WHERE city = ? AND zoom = ? AND source = ? ORDER BY created_at ASC LIMIT -1 OFFSET 5)', (city, zoom, source))

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
    parser.add_argument('-s', '--source', type=str, default='weathernetwork', help='The source to use for the radar images. Can be weathernetwork, windy, or acuweather.')
    parser.add_argument('--mode', type=str, default=None, help='The mode to use for the Windy weather provider.')
    parser.add_argument('--debug', action='store_true', help='If set, run the webdriver in non-headless mode for debugging purposes.')

    args = parser.parse_args()

    db_manager = DatabaseManager(args.db_path)
    db_manager.start()

    fetcher = RadarFetcher(
        args.city, 
        zoom=args.zoom, 
        frames=args.frames, 
        output=args.output, 
        db_queue=db_manager.queue, 
        source=args.source, 
        mode=args.mode, 
        debug=args.debug)
    fetcher.capture_radar()
    fetcher.write_gif()
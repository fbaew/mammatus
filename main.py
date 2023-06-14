import argparse
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import imageio
import os

import requests

def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search/{city}?format=json&addressdetails=0&limit=1"

    response = requests.get(url)
    data = response.json()

    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return float(lat), float(lon)
    else:
        return None, None


# dictionary for city coordinates
city_coordinates = {
    'Calgary': {'lat': 51.0275, 'lng': -114.0498}
    # Add more cities as needed
}

def capture_radar(city, duration, zoom):
    coords = get_coordinates(city)
    lat, lng = coords 
    url = f'https://www.theweathernetwork.com/en/maps/radar?lat={lat}&lng={lng}'
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")

    # setup webdriver
    options = Options()
#    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")  # This will suppress all messages except fatal errors

    driver = webdriver.Chrome(r'chromedriver.exe', options=options)

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

    # Zoom in
    try:
        zoom_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Zoom In"]')))
        for _ in range(zoom):
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
    images = []
    for idx, _ in enumerate(range(duration)):
        print(f'Collecting screenshot {idx+1}/{duration}')
        image = driver.get_screenshot_as_png()
        images.append(imageio.imread(image))
#        time.sleep(1)

    # Assemble the screenshots into a gif
    imageio.mimsave(f'{timestamp}_{city}_radar_z{zoom}.gif', images)

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture weather radar images and assemble them into a gif.')
    parser.add_argument('city', type=str, help='The city to capture the radar images of.')
    parser.add_argument('-d', '--duration', type=int, default=10, help='The duration to capture the radar images for.')
    parser.add_argument('-z', '--zoom', type=int, default=0, help='The zoom level for radar images. Can be 0, 1, 2, 3, or 4.')

    args = parser.parse_args()

    capture_radar(args.city, args.duration, args.zoom)

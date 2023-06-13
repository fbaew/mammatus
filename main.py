import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import imageio
import os

# dictionary for city coordinates
city_coordinates = {
    'Calgary': {'lat': 51.0275, 'lng': -114.0498}
    # Add more cities as needed
}

def capture_radar(city, duration):
    lat, lng = city_coordinates.get(city, city)
    url = f'https://www.theweathernetwork.com/en/maps/radar?lat={lat}&lng={lng}'

    # setup webdriver
    driver = webdriver.Chrome(r'chromedriver.exe')

    try:
        # Navigate to the webpage
        driver.get(url)

        # Wait for page to load
        time.sleep(5)  # Adjust this delay as needed

    except:
        pass

    # Close cookie bar if it is present
    try:
        cookie_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="cookie-bar-close-button"]')))
        cookie_button.click()
    except:
        pass

    # Wait for the play/pause button to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="play-pause-button"]')))

    # Click the play button
    play_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="play-pause-button"]')
    play_button.click()

    # Take screenshots every 1 second for the duration
    images = []
    for _ in range(duration):
        image = driver.get_screenshot_as_png()
        images.append(imageio.imread(image))
        time.sleep(1)

    # Assemble the screenshots into a gif
    imageio.mimsave('radar_output.gif', images)

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture weather radar images and assemble them into a gif.')
    parser.add_argument('city', type=str, help='The city to capture the radar images of.')
    parser.add_argument('-d', '--duration', type=int, default=10, help='The duration to capture the radar images for.')

    args = parser.parse_args()

    capture_radar(args.city, args.duration)

import argparse
import time
from selenium import webdriver
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

    print(f'Capturing radar images for {city}... (url: {url})')
    # setup webdriver
    driver = webdriver.Chrome()

    try:
        # Navigate to the webpage
        driver.get(url)

    except Exception as e:
        pass

capture_radar('Calgary', 10)

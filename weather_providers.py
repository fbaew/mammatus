from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from imageio.core.util import asarray
import imageio
import time

class FrameCapturer(ABC):
    def __init__(self, driver, zoom=0, mode=None):
        self.driver = driver
        self.zoom_level = zoom
        self.mode=mode

    @abstractmethod
    def prep(self):
        pass

    @abstractmethod
    def animate(self):
        pass

    def capture_frame(self):
        image = self.driver.get_screenshot_as_png()
        return imageio.imread(image)

class WeatherNetwork(FrameCapturer):
    def __init__(self, driver, zoom=0, mode='radar'):
        super().__init__(driver)

    def prep(self):
            self.dismiss_cookie_banner()
            self.hide_unwanted_elements()
            self.toggle_fullscreen()
            self.zoom(self.zoom_level)

    def animate(self):
            self.play()



    def dismiss_cookie_banner(self):
        try:
            print('Dismissing cookie banner')
            cookie_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="cookie-bar-close-button"]')))
            cookie_button.click()
        except:
            pass

    def hide_unwanted_elements(self):
        elements_to_hide = ['responsive-header-bar', 'div-gpt-ad-topbanner-short']
        for element in elements_to_hide:
            try:
                print(f'Hiding unwanted elements')
                unwanted_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-testid="{element}"]')))
                self.driver.execute_script("arguments[0].style.visibility='hidden'", unwanted_element)
                print('Done ')
            except:
                pass

    def toggle_fullscreen(self):
        try:
            full_screen_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Toggle Full Screen"]')))
            full_screen_button.click()
        except:
            pass

    def zoom(self, zoom_level):
        if zoom_level > 0:
            try:
                zoom_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Zoom In"]')))
                for _ in range(zoom_level):
                    zoom_button.click()
                    time.sleep(1)  # add delay between each click
            except:
                pass
        elif zoom_level < 0:
            try:
                zoom_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Zoom Out"]')))
                for _ in range(abs(zoom_level)):
                    zoom_button.click()
                    time.sleep(1)  # add delay between each click
            except:
                pass

    def play(self):
        play_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="play-pause-button"]')
        play_button.click()

class Windy(FrameCapturer):
    def __init__(self, driver, zoom=0, mode='wind'):
        super().__init__(driver)
        self.zoom_level = zoom
        self.mode = mode

    def prep(self):
        self.set_mode(self.mode)
        self.zoom(self.zoom_level)
        self.hide_unwanted_elements()
        time.sleep(1)

    def animate(self):
        self.play()

    def set_mode(self, mode):
        # Possible modes
        """
        unfold,radarSat + set,radar
        radar
        satellite set,satellite
        wind
        rain and thunder
        temperature
        clouds
        waves
        air quality
        there are more..."""
        if mode:
            print('Setting mode to ' + mode or 'nada')
        
        if mode == 'satellite':
            sat_fold = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-do="unfold,radarSat"]')))
            sat_fold.click()
            time.sleep(1)
            satellite_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-do="set,satellite"]')))
            satellite_button.click()
            sat_fold.click()

        elif mode == 'radar':
            sat_fold = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-do="unfold,radarSat"]')))
            sat_fold.click()
            time.sleep(1)
            radar_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-do="set,radar"]')))
            radar_button.click()
            sat_fold.click()

        print('done!')

    def dismiss_cookie_banner(self):
        try:
            print('Dismissing cookie banner')
            cookie_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="cookie-banner-close"]')))
            cookie_button.click()
        except:
            pass

    def hide_unwanted_elements(self):
        elements_to_hide = ['search-weather-bg', 'plugin-rhpane', 'rh-icons', 'logo-wrapper']
        for element in elements_to_hide:
            try:
                print(f'Hiding unwanted element with ID: {element}')
                unwanted_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, element)))
                self.driver.execute_script("arguments[0].style.visibility='hidden'", unwanted_element)
                print('Done ')
            except:
                pass

    def zoom(self, zoom_level):
        if zoom_level > 0:
            try:
                zoom_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-do="bcast,zoomIn"]')))
                for _ in range(zoom_level):
                    zoom_button.click()
                    time.sleep(1)  # add delay between each click
            except:
                pass
        elif zoom_level < 0:
            try:
                zoom_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-do="bcast,zoomOut"]')))
                for _ in range(abs(zoom_level)):
                    zoom_button.click()
                    time.sleep(1)  # add delay between each click
            except:
                pass

    def play(self):
        try:
            play_button = self.driver.find_element(By.ID, 'playpause')
            play_button.click()
        except NoSuchElementException:
            play_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-ref="play"]')))
            play_button.click()

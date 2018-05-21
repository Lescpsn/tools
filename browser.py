from copy import deepcopy
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select


class Browser:
    def __init__(self, **kwargs):
        driver_path = kwargs.get('driver_path', 'chromedriver')
        headless = kwargs.get('headless', False)
        no_image = kwargs.get('no_image', False)
        user_agent = kwargs.get('user_agent', '')
        proxy = kwargs.get('proxy', '')
        home_page = kwargs.get('home_page', '')

        options = Options()
        if headless:
            options.add_argument('--headless')
        if no_image:
            option_load_img = {'profile.managed_default_content_settings.images': 2}
            options.add_experimental_option('prefs', option_load_img)
        if user_agent:
            options.add_argument(f'user-agent={user_agent}')
        if proxy:
            options.add_argument(f'--proxy-server=http://{proxy}')
        self.chrome = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        self.chrome.maximize_window()
        if home_page:
            self.chrome.get(home_page)

    def new_window(self, url, timeout=0, switch=True, keep_current_cookie=False):
        self.chrome.set_page_load_timeout(timeout) if timeout else None
        self.chrome.set_script_timeout(timeout) if timeout else None
        if not keep_current_cookie:
            self.chrome.delete_all_cookies()
        self.chrome.execute_script(f'window.open("{url}")')
        if switch:
            self.chrome.close()
            self.chrome.switch_to.window(self.chrome.window_handles[0])

    def get_cookie(self):
        return {item['name']: item['value'] for item in self.chrome.get_cookies()}

    def set_cookie(self, cookie, keep_current_cookie=False):
        if not keep_current_cookie:
            self.chrome.delete_all_cookies()
        for key, value in cookie.items():
            self.chrome.add_cookie({'name': key, 'value': value})

    def get_captcha_as_bytes(self, xpath):
        from PIL import Image

        image_path = 'screen_shoot.png'
        self.chrome.get_screenshot_as_file(image_path)
        element = self.chrome.find_element_by_xpath(xpath)
        x = element.location['x']
        y = element.location['y']
        w = element.size['width']
        h = element.size['height']
        element = Image.open(image_path)
        region = element.crop((x, y, x + w, y + h))
        region.save(image_path)

        with open(image_path, 'rb') as file:
            image_bytes = deepcopy(file.read())
        os.remove(image_path)
        return image_bytes

    def wait_until(self, key_word, timeout=30):
        if timeout <= 0:
            return False
        if key_word not in self.chrome.page_source:
            time.sleep(1)
            return self.wait_until(key_word, timeout - 1)
        return True

    def select_by_value(self, xpath, value):
        select = Select(self.chrome.find_element_by_xpath(xpath))
        select.select_by_value(value)

import time

from appium import webdriver as app_driver


class Android:
    key_code = {
        '0': 7, '1': 8, '2': 9, '3': 10, '4': 11, '5': 12, '6': 13, '7': 14, '8': 15, '9': 16,
        'a': 29, 'b': 30, 'c': 31, 'd': 32, 'e': 33, 'f': 34, 'g': 35, 'h': 36, 'i': 37,
        'j': 38, 'k': 39, 'l': 40, 'm': 41, 'n': 42, 'o': 43, 'p': 44, 'q': 45, 'r': 46,
        's': 47, 't': 48, 'u': 49, 'v': 50, 'w': 51, 'x': 52, 'y': 53, 'z': 54,
        '\'': 75, '@': 77, '\\': 73, ',': 55, '=': 70, '`': 68, '[': 71, '-': 69, '.': 56,
        '+': 81, '#': 18, ']': 72, ';': 74, '/': 76, '*': 17, ' ': '62', '\t': 61
    }

    def __init__(self, device_name, android_version, app_package, app_activity, **kwargs):

        auto_launch = kwargs.get('auto_launch', True)
        appium_address = kwargs.get('appium_address', True)

        desired_capabilities = {
            'platformName': 'Android',
            'platformVersion': android_version,  # 设置系统版本
            'deviceName': device_name,  # 设置设备名（adb devices）
            'appPackage': app_package,  # 设置包名
            'appActivity': app_activity,  # 设置activity
            'unicodeKeyboard': True,  # 支持中文输入
            'resetKeyboard': True,  # 重置输入法（为了启用中文输入）
            # 'replace': True,  # 不知道干啥
            'noReset': True,  # 避免重复安装测试工具
            'noSign': True,  # 避免重签名
            'autoLaunch': auto_launch  # 自动启动desired_cap设置的app
        }
        self.driver = app_driver.Remote(appium_address, desired_capabilities)

    def wait_until(self, key_word, timeout=30):
        if timeout <= 0:
            return False
        if key_word not in self.driver.page_source:
            time.sleep(1)
            return self.wait_until(key_word, timeout - 1)
        return True

    def tap_string(self, string):
        for c in string:
            time.sleep(0.1)
            key = self.key_code.get(c)
            if key is None:
                raise KeyError(f'character {c} not found')
            self.driver.press_keycode(key)

    def find_element_by_keyword(self, keyword, **kwargs):
        id_ = kwargs.get('id_')
        class_name = kwargs.get('class_')
        if id_:
            for element in self.driver.find_elements_by_id(id_):
                if keyword in element.text:
                    return element
        elif class_name:
            for element in self.driver.find_elements_by_class_name(class_name):
                if keyword in element.text:
                    return element
        else:
            raise AttributeError('must send id or class name')

    def long_press(self, element, duration=2):
        x = element.location.get('x')
        y = element.location.get('y')
        self.driver.swipe(x, y, x, y, 1000 * duration)

    def scroll_screen(self):
        width = self.driver.get_window_size()['width']
        height = self.driver.get_window_size()['height']
        self.driver.swipe(width // 2, height * 3 // 4, width // 2, height // 4)

from ctypes import windll
from ctypes import c_wchar_p
from ctypes import c_char_p
from ctypes import c_int
import os

class UU:
    def __init__(self, username, password):
        dll_path = os.path.join(os.path.dirname(__file__), 'uu.dll')
        self.uu = windll.LoadLibrary(dll_path)
        self.username = username
        self.password = password
        # self.code_id = 0
        self.set_timeout()

    def get_score(self):
        getScore = self.uu.uu_getScoreW
        username = c_wchar_p(self.username)
        password = c_wchar_p(self.password)
        return getScore(username, password)

    def login(self):
        setSoftInfo = self.uu.uu_setSoftInfoW
        s_id = c_int(111830)
        s_key = c_wchar_p('adfa045fc2c547aea45362915e1e0450')
        setSoftInfo(s_id, s_key)

        login = self.uu.uu_loginW
        username = c_wchar_p(self.username)
        password = c_wchar_p(self.password)
        user_id = login(username, password)
        return user_id, self.get_score()

    def recognize_by_path(self, image_path, code_type):
        self.login()
        captcha_recognize = self.uu.uu_recognizeByCodeTypeAndPathW
        result = c_wchar_p('                                                  ')  # 申请内存空间
        code_id = captcha_recognize(c_wchar_p(image_path), c_int(code_type), result)
        if code_id <= 0:
            self.report_error(code_id)
            return '', code_id

        code = result.value.split('_')[-1]
        return code, code_id

    def recognize_by_bytes(self, image_bytes, code_type):
        self.login()
        captcha_recognize = self.uu.uu_recognizeByCodeTypeAndBytesW
        result = c_wchar_p('                                                  ')  # 申请内存空间
        code_id = captcha_recognize(c_char_p(image_bytes), c_int(len(image_bytes)), c_int(code_type), result)
        if code_id <= 0:
            self.report_error(code_id)
            return '', code_id

        code = result.value.split('_')[-1]
        return code, code_id

    def set_timeout(self, timeout=10):
        setTimeout = self.uu.uu_setTimeOut
        setTimeout(timeout * 1000)

    def report_error(self, code_id):
        return self.uu.uu_reportError(code_id)


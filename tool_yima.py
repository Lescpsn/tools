import json
import time

import requests


class Yima:
    def __init__(self, token):
        self.api_base = 'http://api.fxhyd.cn/UserInterface.aspx?action='
        self.token = token

    def login(self, username, password):
        api = f'{self.api_base}login&username={username}&password={password}'
        resp = requests.get(api)
        resp.encoding = 'utf-8'
        if 'success' in resp.text:
            status, token = resp.text.split('|')
            return status, token

    def account_info(self):
        api = f'{self.api_base}getaccountinfo&token={self.token}&format=1'
        resp = requests.get(api)
        resp.encoding = 'utf-8'
        if 'success' in resp.text:
            status, account_info = resp.text.split('|')
            return json.loads(account_info)

    def get_phone(self, item_id, special='', retry=3):
        if retry <= 0:
            return
        api = f'{self.api_base}getmobile&itemid={item_id}&token={self.token}{"&mobile=" + special if special else ""}'
        resp = requests.get(api)
        if 'success' in resp.text:
            status, phone = resp.text.split('|')
            return phone
        else:
            return self.get_phone(item_id, special, retry - 1)

    def get_sms(self, phone, item_id, retry=20, interval=3):
        api = f'{self.api_base}getsms&mobile={phone}&itemid={item_id}&token={self.token}&release=1'
        resp = requests.get(api)
        resp.encoding = 'utf-8'
        if 'success' in resp.text:
            status, sms = resp.text.split('|')
            return sms
        else:
            # print(f'get sms fail, retry in {interval}s')
            if retry > 0:
                time.sleep(interval)
                return self.get_sms(phone, item_id, retry=retry - 1)

    def release(self, phone, item_id):
        api = f'{self.api_base}release&mobile={phone}&itemid={item_id}&token={self.token}'
        requests.get(api)

    def add_ignore(self, phone, item_id):
        api = f'{self.api_base}addignore&mobile={phone}&itemid={item_id}&token={self.token}'
        requests.get(api)

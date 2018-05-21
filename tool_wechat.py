import time
import threading

import requests


class WechatAlarm:
    def __init__(self, corpid, corpsecret, agentid):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid

        # update access token in child thread
        thread_update = threading.Thread(target=self.__get_token)
        thread_update.daemon = True
        thread_update.start()

        # waiting for initialization
        while not hasattr(self, 'access_token'):
            time.sleep(1)

    def __get_token(self):
        while True:
            try:
                url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}'
                resp = requests.get(url)
                self.access_token = resp.json().get('access_token')
                expire = resp.json().get('expires_in')
                time.sleep(expire * 0.9)
            except:
                return self.__get_token()

    def send_alarm(self, message):
        try:
            url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}'
            data = {
                'touser': '@all',
                'msgtype': 'text',
                'agentid': self.agentid,
                'text': {
                    'content': message
                },
            }
            requests.post(url, json=data)
        except:
            pass

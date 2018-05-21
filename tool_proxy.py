import time
import re
import random
import threading

import requests
import redis as pyredis

redis = pyredis.StrictRedis(db=14)


class Data5u:
    def __init__(self, token_list, expire_handler=None):
        self.token_list = token_list
        self.expire_handler = expire_handler

        # update proxy in child thread
        thread_update = threading.Thread(target=self.__get_proxy)
        thread_update.daemon = True
        thread_update.start()

        # waiting for initialization
        while not redis.keys():
            time.sleep(1)

    def __get_proxy(self):
        while True:
            time.sleep(1)
            try:
                for token in self.token_list:
                    url = f'http://api.ip.data5u.com/dynamic/get.html?order={token}&ttl'
                    resp = requests.get(url, timeout=10)
                    if 'too many request' in resp.text:
                        continue
                    elif '充值' in resp.text:
                        if self.expire_handler:
                            self.expire_handler(token)
                        print(f'data5u >> token expire: {token}')
                        self.token_list.remove(token)
                    else:
                        ip, port, timeout = re.findall(r'(\d+.\d+.\d+.\d+):(\d+),(\d+)', resp.text)[0]
                        key = f'{ip}:{port}'
                        if redis.exists(key):
                            continue
                        redis.set(key, 1)
                        redis.expire(key, int(timeout) // 1000)
                        print(f'data5u >> {ip}:{port}')
            except:
                continue

    @staticmethod
    def get_proxy():
        try:
            ip, port = random.choice([key.decode('utf-8') for key in redis.keys()]).split(':')
            return {
                'http': f'http://{ip}:{port}',
                'https': f'http://{ip}:{port}',
            }
        except:
            return None


class Abuyun:
    def __init__(self, username, password, host, port):
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    def get_proxy(self):
        return {
            'http': f'http://{self.username}:{self.password}@{self.host}:{self.port}',
            'https': f'http://{self.username}:{self.password}@{self.host}:{self.port}'
        }

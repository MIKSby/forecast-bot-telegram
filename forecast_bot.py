import hashlib
import os
from typing import List

import requests
from requests import Response

from telegram import TelegramApi, delay


class ForecastBot(TelegramApi):
    def __init__(self, token, img_urls: List[str], followers_file: str) -> None:
        super().__init__(token)
        self.state = {}
        self.img_urls = img_urls
        self.followers_file = followers_file
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9;'
                                      ' rv:45.0) Gecko/20100101 Firefox/45.0',
                        'Connection': 'close'}

    def check_forecast(self) -> bool:
        for img in self.img_urls:
            old_hash = self.state[f'{self._get_fname(img)}_md5']
            if old_hash == self.find_hash(self._request(img).content):
                return False
        return True

    def is_available(self) -> bool:
        for img in self.img_urls:
            if not os.path.isfile(self._get_fname(img)):
                return False
        return True

    def send(self) -> None:
        with open(self.followers_file, 'r') as members:
            for member in members:
                member_id = member.strip()
                self.send_message(chat_id=member_id,
                                  text='Прогноз обновлен⬇️')
                for url in self.img_urls:
                    self.send_photo(chat_id=member_id,
                                    photo=self.state[self._get_fname(url)].content)

    def save(self) -> None:
        for img in self.img_urls:
            fname = self._get_fname(img)
            r = requests.get(img, headers=self.headers)
            if r.status_code == 200:
                with open(fname, 'wb') as file:
                    file.write(r.content)
                self.state[fname] = r
                self.state[f'{fname}_md5'] = self.find_hash(r.content)

    @delay
    def _request(self, url: str) -> Response:
        return requests.get(url, headers=self.headers)

    @staticmethod
    def _get_fname(url: str) -> str:
        return url.split('/')[-1]

    @staticmethod
    def find_hash(content: str) -> str:
        md5 = hashlib.md5()
        md5.update(content)
        return md5.hexdigest()

    def add_new_followers(self) -> None:
        response = self.get_updates()
        result = response.json().get('result')
        if result:
            senders = {str(x['message']['chat']['id']) for x in result}
            with open(self.followers_file, 'r') as old_file:
                old_followers = {x.strip() for x in old_file}

            new_followers = senders.difference(old_followers)
            if new_followers:
                print(f'new followers: {new_followers}')
                with open(self.followers_file, 'w') as new_file:
                    for follower_id in {*old_followers, *new_followers}:
                        new_file.write(f'{follower_id}\n')
                for follower in new_followers:
                    self.send_message(chat_id=follower,
                                      text='Прогноз обновлен⬇️')
                    for url in self.img_urls:
                        self.send_photo(chat_id=follower,
                                        photo=self.state[self._get_fname(url)].content)

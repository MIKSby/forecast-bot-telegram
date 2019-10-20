import hashlib
import requests
from telegram import TelegramApi, delay
import os


class ForecastBot(TelegramApi):
    def __init__(self, token, img_urls, followers):
        super().__init__(token)
        self.state = {}
        self.img_urls = img_urls
        self.followers = followers
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

    def send(self):
        with open('members.txt', 'r') as members:
            for member in members:
                member_id = member.strip()
                self.send_message(chat_id=member_id,
                                  text='Прогноз обновлен⬇️')
                for url in self.img_urls:
                    self.send_photo(chat_id=member_id,
                                    photo=self.state[self._get_fname(url)].content)

    def save(self):
        for img in self.img_urls:
            fname = self._get_fname(img)
            r = requests.get(img, headers=self.headers)
            if r.status_code == 200:
                with open(fname, 'wb') as file:
                    file.write(r.content)
                self.state[fname] = r
                self.state[f'{fname}_md5'] = self.find_hash(r.content)

    @delay
    def _request(self, url: str):
        return requests.get(url, headers=self.headers)

    @staticmethod
    def _get_fname(url: str) -> str:
        return url.split('/')[-1]

    @staticmethod
    def find_hash(content: str) -> str:
        md5 = hashlib.md5()
        md5.update(content)
        return md5.hexdigest()

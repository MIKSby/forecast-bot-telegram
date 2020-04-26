import hashlib
import os
import re
import time
from typing import List, Optional

import requests
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from pyrogram import Client
from requests import Response

from telegram import TelegramApi, delay


def create_temp_image(temp: str) -> Image:
    assert isinstance(temp, str)
    image = Image.new('RGBA', (640, 640), (255, 255, 255, 255))
    font = ImageFont.truetype('fonts/Roboto-Medium.ttf', 175)
    d = ImageDraw.Draw(image)
    d.text((5, 200), temp, font=font, fill=(0, 0, 0, 255))
    image_name = 'bot_pic.png'
    image.save(image_name)
    return image_name


class ForecastBot(TelegramApi):
    def __init__(self, token, api_id, api_hash, img_urls: List[str], followers_file: str) -> None:
        super().__init__(token)
        self.api_id = api_id
        self.api_hash = api_hash
        self.telegram_client = Client('session', api_hash=self.api_hash, api_id=self.api_id)
        self.telegram_client.start()
        self.telegram_client.get_dialogs()
        self._bot_father_chat_id = 93372553
        self._current_temp = 0.0
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

    def update_pic_temp(self):
        new_temp = self.get_current_temp()
        if new_temp is None:
            return None
        image_name = create_temp_image(new_temp)
        self.telegram_client.send_message(text='/setuserpic', chat_id=self._bot_father_chat_id)
        time.sleep(3)
        self.telegram_client.send_message(text='@PogodaTheBot', chat_id=self._bot_father_chat_id)
        time.sleep(3)
        self.telegram_client.send_photo(photo=image_name, chat_id=self._bot_father_chat_id)

    @staticmethod
    def get_current_temp() -> Optional[str]:
        try:
            html_doc: bytes = requests.get('http://www.belmeteo.net/').content
        except requests.ConnectionError:
            return None
        soup = BeautifulSoup(html_doc, 'html.parser')
        left_panel = soup.find_all('div', class_='leftSideBar')
        try:
            current_temp_text = left_panel[0].ul.li.b.text
        except IndexError:
            return None
        current_temp_find = re.findall(r'.\d+[.]\d..', current_temp_text)
        assert len(current_temp_find) == 1
        current_temp = current_temp_find[0]
        if '-' not in current_temp:
            return f'+{current_temp[1:]}'
        else:
            return current_temp

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
    def find_hash(content: bytes) -> str:
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

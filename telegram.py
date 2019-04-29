import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from time import sleep


def delay(func):
    def wrap(*args, **kwargs):
        sleep(1)
        while True:
            try:
                response = func(*args, **kwargs)
                if response.status_code == 200:
                    return response
                else:
                    print(f'Warning! Response code is {response.status_code}')
                    sleep(30)
            except (ConnectionError, ConnectTimeout) as exc:
                print('Connection error!', exc)
                sleep(10)
    return wrap


class TelegramApi:
    def __init__(self, token):
        self.tg_api_url = f'https://api.telegram.org/bot{token}/'

    @delay
    def get_updates(self):
        return requests.get(url=f'{self.tg_api_url}getUpdates')

    @delay
    def send_message(self, chat_id, text):
        return requests.post(url=f'{self.tg_api_url}sendMessage',
                             data={'chat_id': chat_id,
                                   'text': text})

    @delay
    def send_photo(self, chat_id, photo):
        return requests.post(url=f'{self.tg_api_url}sendPhoto',
                             data={'chat_id': chat_id},
                             files={'photo': photo})

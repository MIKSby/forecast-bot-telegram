from time import sleep

import requests
from requests import Response
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout


def delay(func):
    def wrap(*args, **kwargs):
        sleep(5)
        while True:
            try:
                response = func(*args, **kwargs)
                if response.status_code == 200:
                    return response
                else:
                    print(f'Warning! Response code is {response.status_code}')
                    response_json = response.json()
                    print(response_json)
                    if response_json.get('ok', None) is False:
                        print('------------------------------')
                        print(response_json['description'], 'user:', kwargs['chat_id'])
                        return None
            except (ConnectionError, ConnectTimeout, ReadTimeout) as exc:
                print('Connection error!', exc)
                sleep(10)

    return wrap


class TelegramApi:
    def __init__(self, token: str) -> None:
        self.tg_api_url = f'https://api.telegram.org/bot{token}/'

    @delay
    def get_updates(self) -> Response:
        return requests.get(url=f'{self.tg_api_url}getUpdates')

    @delay
    def send_message(self, chat_id: str, text: str) -> Response:
        return requests.post(url=f'{self.tg_api_url}sendMessage',
                             data={'chat_id': chat_id,
                                   'text': text})

    @delay
    def send_photo(self, chat_id: str, photo: str) -> Response:
        return requests.post(url=f'{self.tg_api_url}sendPhoto',
                             data={'chat_id': chat_id},
                             files={'photo': photo})

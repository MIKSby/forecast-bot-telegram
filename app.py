import sys
import time

from forecast_bot import ForecastBot

try:
    from secret import telegram_token, api_hash, api_id
except ModuleNotFoundError:
    print('Need create file "secret.py"')
    sys.exit(1)

forecast = ForecastBot(
    token=telegram_token,
    api_id=api_id,
    api_hash=api_hash,
    img_urls=['http://www.pogoda.by/mg/366/noaa_T26850.gif', 'http://www.pogoda.by/mg/366/noaa_W26850.gif'],
    followers_file='members.txt'
)

if not forecast.is_available():
    print(f'No forecast, downloading - {time.ctime()}')
    forecast.save()
    forecast.send()
else:
    print(f'Forecast loaded, start checking - {time.ctime()}')
    forecast.save()

while True:
    forecast.update_pic_temp()
    forecast.add_new_followers()
    if forecast.check_forecast():
        forecast.save()
        forecast.send()
        print(f'Forecast updated - {time.ctime()}')
    time.sleep(600)

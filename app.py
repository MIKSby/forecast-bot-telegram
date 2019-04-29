from forecast_bot import ForecastBot
from secret import telegram_token
import time


forecast = ForecastBot(token=telegram_token,
                       img_urls=['http://www.pogoda.by/mg/366/egrr_T26850.gif',
                                 'http://www.pogoda.by/mg/366/egrr_W26850.gif'],
                       followers='members.txt')


if not forecast.is_available():
    forecast.save()
    forecast.send()
    print(f'No forecast, downloading - {time.ctime()}')
else:
    print(f'Forecast loaded, start checking - {time.ctime()}')
    forecast.save()

while True:
    if forecast.check_forecast():
        forecast.save()
        forecast.send()
        print(f'Forecast updated - {time.ctime()}')
    time.sleep(60)

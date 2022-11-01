import requests
import json

API_KEY = "1d3437bd88ae64535e9f50b96b3d403f"


def get_future_weather(lat, lon, days):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}&lang=ua"
    response = json.loads(requests.get(url).content)
    res = []
    for day in range(0, len(response['list']), 8):
        res.append({'temp': response['list'][day]['main']['temp'],
                    'maxtemp': response['list'][day]['main']['temp_max'],
                    'mintemp': response['list'][day]['main']['temp_min']})
    return res[:days]


# get_future_weather("48.918460", "24.719267", 1)



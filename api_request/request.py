import json

import requests

from settings import api_config


def get_city_coord(city: str) -> str:

    geocode_url = 'https://geocode-maps.yandex.ru/1.x'
    payload = {'geocode': city, 'apikey': api_config.geo_key, 'format': 'json'}
    r = requests.get(geocode_url, params=payload)
    geo = json.loads(r.text)

    return geo['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']


def get_weather(city: str) -> str:

    weather_url = 'https://api.weather.yandex.ru/v2/forecast'
    coord = get_city_coord(city).split()
    payload = {'lat': coord[0], 'lon': coord[1], 'lang': 'ru_RU'}
    r = requests.get(weather_url, params=payload, headers=api_config.weather_key)
    weather_data = json.loads(r.text)

    return weather_data['fact']

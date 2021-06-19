import requests
from geopy import distance
from environs import Env


env = Env()
env.read_env()
yandex_apikey = env('YANDEX_APIKEY')


def get_distance(lat_pizzeria, lon_pizzeria, lat_user, lon_user):
    pizzeria_location = (lat_pizzeria, lon_pizzeria)
    user_location = (lat_user, lon_user)
    distance_user = distance.distance(pizzeria_location, user_location).m
    return int(distance_user)


def fetch_coordinates(place, apikey):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place,
              "apikey": apikey,
              "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def get_user_location(bot, update):

    message = update.message['text']
    if message is None:
        message = update.message
        lat, lon = (message.location.latitude, message.location.longitude)
    else:
        places = fetch_coordinates(message, yandex_apikey)
        found_places = places['response']['GeoObjectCollection']['featureMember']
        if found_places:
            most_relevant = found_places[0]
            lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        else:
            update.message.reply_text('Не можем определить ваш адрес\n'
                                      'Попробуйте еще раз!')
            return "WAITING_LOC"
    return lat, lon

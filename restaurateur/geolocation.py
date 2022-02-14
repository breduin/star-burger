import requests

from collections import OrderedDict
from geopy.distance import great_circle as GC

from django.conf import settings
from django.shortcuts import render

from foodcartapp.models import Restaurant, Order


APIKEY = settings.YANDEX_MAPS_API_KEY


def fetch_coordinates(address, apikey=APIKEY):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_distance(address1, address2):
    coord1 = fetch_coordinates(address1)
    coord2 = fetch_coordinates(address2)
    if all([coord1, coord2]):
        return GC(coord1, coord2).km
    return None


def get_restaurants_distances(restaurants, order) -> dict:

    # FIXME объединить код для получения координат order и restaurant (ContentType?)
     
    if not all([order.latitude, order.longitude]):
        if order_coordinates:=fetch_coordinates(order.address):
            latitude, longitude = order_coordinates
        else:
            return {}
        order.latitude = latitude
        order.longitude = longitude
        order.save()
        order_coords = (latitude, longitude)
    else:
        order_coords = (order.latitude, order.longitude)

    restaurants_distances = {}
    for restaurant in restaurants:
        if not all([restaurant.latitude, restaurant.longitude]):
            if restaurant_coordinates:=fetch_coordinates(restaurant.address):
                latitude, longitude = restaurant_coordinates
                restaurant.latitude = latitude
                restaurant.longitude = longitude
                restaurant.save()
                restaurant_coords = (latitude, longitude)
            else:
                continue
        else:
            restaurant_coords = (restaurant.latitude, restaurant.longitude)

        distance = GC(order_coords, restaurant_coords).km
        restaurants_distances[restaurant] = distance

    restaurants_distances_ordered = dict(
        sorted(restaurants_distances.items(), key=lambda x: x[1])
        )

    return restaurants_distances_ordered

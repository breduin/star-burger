import requests
from collections import OrderedDict
from decimal import *
from geopy.distance import great_circle as GC

from django.shortcuts import render
from django.conf import settings

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
    return GC(coord1, coord2).km


def get_restaurants_distances(restaurants, order) -> dict:

    # FIXME объединить код для получения координат order и restaurant (ContentType?)
     
    if not all([order.latitude, order.longitude]):
        latitude, longitude = fetch_coordinates(order.address)
        order.latitude = latitude
        order.longitude = longitude
        Order.objects.filter(id=order.id).update(latitude=latitude, 
                                                 longitude=longitude
                                                 )
        order_coords = (latitude, longitude)
    else:
        order_coords = (order.latitude, order.longitude)

    restaurants_distances = {}
    for restaurant in restaurants:
        if not all([restaurant.latitude, restaurant.longitude]):
            latitude, longitude = fetch_coordinates(restaurant.address)
            restaurant.latitude = latitude
            restaurant.longitude = longitude
            Restaurant.objects.filter(id=restaurant.id).update(latitude=latitude, 
                                                           longitude=longitude
                                                           )
            restaurant_coords = (latitude, longitude)
        else:
            restaurant_coords = (restaurant.latitude, restaurant.longitude)
        
        distance = GC(order_coords, restaurant_coords).km
        restaurants_distances[distance] = restaurant
    
    restaurants_distances_ordered = OrderedDict()
    while len(restaurants_distances) > 0:
        distances = restaurants_distances.keys()
        min_distance = min(distances)
        restaurant = restaurants_distances.pop(min_distance)
        restaurants_distances_ordered[restaurant] = min_distance

    return restaurants_distances_ordered

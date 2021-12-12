from django.db import models

from .models import Restaurant, Product, RestaurantMenuItem


def get_restaurants_with_order_products(order_id: int) -> models.QuerySet:
    """Return restaurants with complete set of products in order with ID=order_id."""
    restaurants = Restaurant.objects.prefetch_related('menu_items').order_by('name')
    products = Product.objects.prefetch_related('order_items')
    products_in_order = products.filter(
        order_items__order=order_id,
        ).order_by('name').values_list('id')
    menu_items = RestaurantMenuItem.objects.all()

    is_product_in_restaurant = {}
    for restaurant in restaurants:
        is_product_in_restaurant[
            restaurant.id
            ] = [
                item.availability for item in menu_items.filter(
                    product__in=products_in_order, restaurant=restaurant,
                    ).order_by('product__name')
                    ]

    restaurants_with_complete_set = [
        restaurant.id for restaurant in restaurants if all(
            is_product_in_restaurant[restaurant.id]
            )
            ]
    return restaurants.filter(id__in=restaurants_with_complete_set)







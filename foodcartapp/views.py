import json
from loguru import logger

from django.http import JsonResponse
from django.templatetags.static import static

from .models import Product, Order, OrderProductItem


logger.add('logs/star-burger.log', format="{time} {level} {message}", rotation="1 MB", level='ERROR')


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    try:
        data = json.loads(request.body.decode())
    except ValueError:
        return JsonResponse({
            'error': 'Ошибка данных',
        })

    order_raw = data.copy()
    del order_raw['products']

    order = Order.objects.create(**order_raw)

    products = data['products']
    for product_item in products:
        product_id = product_item['product']
        product_quantity = product_item['quantity']
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
            'error': 'Такого продукта не существует',
            })
        order_product_item = OrderProductItem.objects.create(product=product,
                                                             quantity=product_quantity,
                                                             order=order,
                                                             )

    return JsonResponse({})

import json
from loguru import logger
import phonenumbers

from django.http import JsonResponse
from rest_framework.response import Response
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework import status

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


def validate_data_from_frontend(data: dict) -> ([str, None], [status, None]):

    # Checks the required fields are presented.
    required_fields = [
        'products', 'firstname', 'lastname', 'phonenumber', 'address',
        ]
  
    are_required_fields_in_data = {x: x in data.keys() for x in required_fields}
    if not all(are_required_fields_in_data.values()):
        return f'Required fields lack: {[x for x in required_fields if not are_required_fields_in_data[x] ]}', \
            status.HTTP_417_EXPECTATION_FAILED
    
    # Checks the not nullable fields are not null.
    non_null_fields = [
        'products', 'firstname', 'lastname', 'phonenumber', 'address',
        ]  
    are_fields_not_null = {x: bool(data[x]) for x in non_null_fields}
    if not all(are_fields_not_null.values()):
        return f'Fields are empty: {[x for x in non_null_fields if not are_fields_not_null[x] ]}', \
            status.HTTP_417_EXPECTATION_FAILED

    # Checks the product field is list
    products = data['products']
    if not isinstance(products, list):
        return '"Products" field must be of list type.', status.HTTP_406_NOT_ACCEPTABLE

    # Checks the products exist
    products = data['products']
    for product_item in products:
        try:
            product_id = product_item['product']
            product_quantity = product_item['quantity']
            product = Product.objects.get(id=product_id)
        except KeyError:
            return f'No product or its quantity in products list.', \
                status.HTTP_406_NOT_ACCEPTABLE
        except Product.DoesNotExist:
            return f'The product with id={product_id} does not exist.', \
                status.HTTP_404_NOT_FOUND

    # Checks the phone number
    phonenumber = data['phonenumber']
    try:
        parsed_phonenumber = phonenumbers.parse(phonenumber, None)
    except phonenumbers.phonenumberutil.NumberParseException as e:
        return f'Phone field: {e._msg}', status.HTTP_406_NOT_ACCEPTABLE
    if not phonenumbers.is_valid_number(parsed_phonenumber):
        return 'Phone number is invalid', status.HTTP_406_NOT_ACCEPTABLE


    # Checks the firstname field is string
    firstname = data['firstname']
    if not isinstance(firstname, str):
        return '"firstname" field must be of str type.', status.HTTP_406_NOT_ACCEPTABLE

    return None, None


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
    except ValueError:
        return JsonResponse({
            'error': 'Data error',
        })

    validation_error, error_status = validate_data_from_frontend(data)
    if validation_error:
        return Response({
            'error': validation_error,
        },
        status=error_status
        )

    order_raw = data.copy()
    del order_raw['products']
    order = Order.objects.create(**order_raw)

    products = data['products']
    for product_item in products:
        product_id = product_item['product']
        product_quantity = product_item['quantity']
        product = Product.objects.get(id=product_id)
        order_product_item = OrderProductItem.objects.create(product=product,
                                                             quantity=product_quantity,
                                                             order=order,
                                                             )

    return Response({})

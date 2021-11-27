from rest_framework.serializers import ModelSerializer, ListField
from .models import Order, OrderProductItem, Product


class OrderProductItemSerializer(ModelSerializer):

    class Meta:
        model = OrderProductItem
        fields = [
            'product',
            'quantity'
            ]    


class OrderSerializer(ModelSerializer):
    products = OrderProductItemSerializer(many=True, 
                                          allow_empty=False, 
                                          write_only=True
                                          )

    class Meta:
        model = Order 
        fields = [
            'products',
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address'
            ]


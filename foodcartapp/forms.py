from django import forms
from .models import Order
from .querysets import get_restaurants_with_order_products


class OrderAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order = self.instance
        self.fields['restaurant'].queryset = get_restaurants_with_order_products(order.id)

    class Meta:
        model = Order
        fields = '__all__'

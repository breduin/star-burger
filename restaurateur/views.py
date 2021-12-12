from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from django.db.models import Sum, F, Q, Count

from foodcartapp.models import Product, Restaurant, Order, OrderProductItem, RestaurantMenuItem
from restaurateur.geolocation import get_restaurants_distances


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = Restaurant.objects.prefetch_related('menu_items').order_by('name')
    products = Product.objects.prefetch_related('menu_items')

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.prefetch_related('menu_items').order_by('name'),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    orders = Order.summed.prefetch_related('product_items__product').all()
    all_restaurants = Restaurant.objects.prefetch_related('menu_items').all()

    products_in_restaurants = {}
    for restaurant in all_restaurants:
        products_in_restaurant = restaurant.menu_items.filter( 
            availability=True
            ).values_list('product__id', flat=True)
        products_in_restaurants[restaurant] = products_in_restaurant
    
    distances = {}
    for order in orders:
        products_in_order = order.product_items.all()
        restaurants_with_all_order_products = [
            r for r in all_restaurants if all(
                [p.product.id in products_in_restaurants[r] for p in products_in_order]) 
            ]   

        distances[order.id] = get_restaurants_distances(
            restaurants_with_all_order_products, 
            order
            )
   
    return render(request, template_name='order_items.html', context={
        'orders': orders,
        'distances': distances,
    })

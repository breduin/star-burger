from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order, OrderProductItem
from .forms import OrderAdminForm


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


class OrderItemsInline(admin.TabularInline):
    model = OrderProductItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer_name',
                    'address',
                    'phonenumber',
                    'amount',
                    'created_at',
                    'called_at',
                    'delivered_at',
                    'payment_method',
                    ]
    inlines = [OrderItemsInline, ]
    form = OrderAdminForm

    def response_change(self, request, obj):
        default_response = super().response_change(request, obj)
        if not 'next' in request.GET:
            return default_response

        # Clearing the messages
        storage = messages.get_messages(request)
        for message in storage:
            _ = message

        url = request.GET['next']
        if url_has_allowed_host_and_scheme(url, settings.ALLOWED_HOSTS):
            return redirect(url)
        return default_response
            

    def save_model(self, request, obj, form, change):
        if not change:
            super().save_model(request, obj, form, change)
            
        previous_address = Order.objects.get(id=obj.id).address
        current_address = obj.address
        if previous_address != current_address:
            obj.latitude = None
            obj.longitude = None
        super().save_model(request, obj, form, change)

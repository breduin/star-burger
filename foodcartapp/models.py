from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, CharField
from django.db.models.functions import Concat
from django.db.models import OuterRef, Subquery
from django.contrib import admin

from .validators import lat_validators, lng_validators


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    latitude = models.FloatField(validators=lat_validators,
                                 verbose_name='Широта', 
                                 null=True,
                                 blank=True,
                                 )
    longitude = models.FloatField(validators=lng_validators,
                                  verbose_name='Долгота',
                                  null=True,
                                  blank=True,
                                  )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        default='',
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderProductItem(models.Model):
    order = models.ForeignKey('Order',
                              verbose_name='заказ',
                              related_name='items',
                              on_delete=models.CASCADE,
                              )
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                verbose_name='продукт',
                                related_name='items',
                                )
    product_price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )                           
    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'позиция в заказе'
        verbose_name_plural = 'позиции в заказе'

    def __str__(self):
        return f'{self.order} - {self.product.name}'


class OrderManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().annotate(
            sum=Sum(F('items__product_price') * F('items__quantity'))
            )


class Order(models.Model):

    STATUSES = [
        ('unprocessed', 'необработанный'),
        ('delivering', 'доставляется'),
        ('completed', 'выполнен'),
    ]

    PAYMENT_METHOD = [
        ('cash', 'наличный'),
        ('cashless', 'безналичный'),
        ('credit', 'кредит'),
    ]

    firstname = models.CharField('Имя заказчика', 
                                 max_length=32
                                 )
    lastname = models.CharField('Фамилия заказчика', 
                                max_length=32
                                )
    phonenumber = PhoneNumberField('Телефон заказчика', db_index=True)

    address = models.CharField('Адрес доставки', 
                               max_length=255
                               )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Время создания',
                                      db_index=True,
                                      )
    updated_at = models.DateTimeField(auto_now=True, 
                                      verbose_name='Время редактирования',
                                      db_index=True,
                                      )
    called_at = models.DateTimeField(verbose_name='Дата и время звонка клиенту', 
                                     null=True, 
                                     blank=True,
                                     db_index=True,
                                     )
    delivered_at = models.DateTimeField(verbose_name='Дата и время доставки клиенту',
                                        null=True, 
                                        blank=True,
                                        db_index=True,
                                        )    
    status = models.CharField('Статус', 
                              max_length=32,
                              choices=STATUSES,
                              default='unprocessed',
                              db_index=True,
                              )
    payment_method = models.CharField('Способ оплаты', 
                                      max_length=32,
                                      choices=PAYMENT_METHOD,
                                      db_index=True,
                                      )
    comment = models.TextField('Комментарий',
                               blank=True,
                               )    
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='Ресторан',
        help_text='Выберите ресторан для исполнения заказа',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )           
    latitude = models.FloatField(validators=lat_validators,
                                 verbose_name='Широта',
                                 null=True,
                                 blank=True,
                                 )
    longitude = models.FloatField(validators=lng_validators,
                                  verbose_name='Долгота',
                                  null=True,
                                  blank=True,
                                  )

    objects = OrderManager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    @admin.display(description='Сумма заказа')
    def amount(self):
        return self.sum

    @admin.display(description='Имя заказчика')
    def customer_name(self):
        return f'{self.firstname} {self.lastname}'

    def __str__(self):
        return f'{self.firstname} {self.lastname} > {self.address} '


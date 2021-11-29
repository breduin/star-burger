from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from django.contrib import admin


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
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
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):

    STATUSES = [
        ('unprocessed', 'необработанный'),
        ('delivering', 'доставляется'),
        ('completed', 'выполнен'),
    ]

    firstname = models.CharField('Имя заказчика', 
                                 max_length=32
                                 )
    lastname = models.CharField('Фамилия заказчика', 
                                max_length=32
                                )
    phonenumber = PhoneNumberField('Телефон заказчика')
    address = models.CharField('Адрес доставки', 
                               max_length=255
                               )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Время создания'
                                      )
    updated_at = models.DateTimeField(auto_now=True, 
                                      verbose_name='Время редактирования'
                                      )
    called_at = models.DateTimeField(verbose_name='Дата и время звонка клиенту', 
                                     null=True, 
                                     blank=True,
                                     )
    delivered_at = models.DateTimeField(verbose_name='Дата и время доставки клиенту',
                                        null=True, 
                                        blank=True,
                                        )    
    status = models.CharField('Статус', 
                              max_length=32,
                              choices=STATUSES,
                              default='unprocessed'
                              )

    comment = models.TextField('Комментарий',
                               default='',
                               blank=True,
                               )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    @admin.display(description='Сумма заказа')
    def amount(self):
        return self.product_items.all().aggregate(sum=
                    Sum(F('product_price') * F('quantity')))['sum']

    @admin.display(description='Имя заказчика')
    def customer_name(self):
        return f'{self.firstname} {self.lastname}'           

    def __str__(self):
        return f'{self.firstname} {self.lastname} > {self.address} '


class OrderProductItem(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name='заказ',
                              related_name='product_items',
                              on_delete=models.CASCADE,
                              )
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                verbose_name='продукт',
                                )
    product_price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )                           
    quantity = models.PositiveSmallIntegerField(verbose_name='количество')

    class Meta:
        verbose_name = 'позиция в заказе'
        verbose_name_plural = 'позиции в заказе'

    def __str__(self):
        return f'{self.order} - {self.product.name}'

# Generated by Django 3.2 on 2021-11-28 10:34

import django.core.validators
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_rename_phone_order_phonenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproductitem',
            name='product_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(max_length=255, verbose_name='Адрес доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='Телефон заказчика'),
        ),
    ]

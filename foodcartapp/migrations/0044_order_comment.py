# Generated by Django 3.2 on 2021-11-29 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default='', verbose_name='Комментарий'),
        ),
    ]

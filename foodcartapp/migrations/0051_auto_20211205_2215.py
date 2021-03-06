# Generated by Django 3.2 on 2021-12-05 19:15

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_auto_20211130_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата и время звонка клиенту'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата и время доставки клиенту'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'наличный'), ('cashless', 'безналичный'), ('credit', 'кредит')], db_index=True, default='cashless', max_length=32, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='Телефон заказчика'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('unprocessed', 'необработанный'), ('delivering', 'доставляется'), ('completed', 'выполнен')], db_index=True, default='unprocessed', max_length=32, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время редактирования'),
        ),
    ]

# Generated by Django 3.2 on 2021-11-29 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20211129_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'наличный'), ('cashless', 'безналичный'), ('credit', 'кредит')], default='cashless', max_length=32, verbose_name='Способ оплаты'),
        ),
    ]

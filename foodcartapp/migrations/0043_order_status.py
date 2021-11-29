# Generated by Django 3.2 on 2021-11-29 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20211128_1045'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('unprocessed', 'необработанный'), ('delivering', 'доставляется'), ('completed', 'выполнен')], default='unprocessed', max_length=32, verbose_name='Статус'),
        ),
    ]

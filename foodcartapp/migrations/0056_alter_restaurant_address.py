# Generated by Django 3.2 on 2022-02-12 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_auto_20220212_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='address',
            field=models.CharField(max_length=100, verbose_name='адрес'),
        ),
    ]

# Data maigration to fill out the product price in OrderProductItem

from django.db import migrations


class Migration(migrations.Migration):

    def fill_product_price(apps, schema_editor):
        Product = apps.get_model('foodcartapp', 'Product')
        OrderProductItem = apps.get_model('foodcartapp', 'OrderProductItem')

        for order_item in OrderProductItem.objects.all():
            order_item.product_price = order_item.product.price
            order_item.save()

    dependencies = [
        ('foodcartapp', '0041_auto_20211128_1034'),
    ]

    operations = [
        migrations.RunPython(fill_product_price),
    ]

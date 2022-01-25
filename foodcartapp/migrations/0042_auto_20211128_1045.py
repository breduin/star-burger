# Data maigration to fill out the product price in OrderProductItem

from django.db import migrations
from django.db.models import Subquery, OuterRef


class Migration(migrations.Migration):

    def fill_product_price(apps, schema_editor):
        Product = apps.get_model('foodcartapp', 'Product')
        OrderProductItem = apps.get_model('foodcartapp', 'OrderProductItem')

        OrderProductItem.objects.update(
            product_price=Subquery(
                OrderProductItem.objects.filter(
                    pk=OuterRef('pk')
                    ).values('product__price')[:1]
                )
            )

    dependencies = [
        ('foodcartapp', '0041_auto_20211128_1034'),
    ]

    operations = [
        migrations.RunPython(fill_product_price),
    ]

# Generated manually

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0005_cartitem_order_orderitem_delete_brand_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
    ]

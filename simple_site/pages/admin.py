from django.contrib import admin
from .models import (
    SiteUser,
    Product,
    Category,
    CartItem,
    Order,
    OrderItem,
)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "stock", "category")
    list_filter = ("category",)
    search_fields = ("title",)


def register_pages_models(site):
    """Register all pages models with the given admin site (used by custom dashboard admin)."""
    site.register(Product, ProductAdmin)
    site.register(Category)
    site.register(SiteUser)
    site.register(CartItem)
    site.register(Order)
    site.register(OrderItem)



from django.contrib import admin
from owners.products.models import StoreProductModel, ProductStatusModel
# Register your models here.

admin.site.register(ProductStatusModel)
admin.site.register(StoreProductModel)

from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(OwnerModel)
admin.site.register(OwnerStoreModel)
admin.site.register(StoreProductModel)
admin.site.register(ProductStatusModel)
from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import Proveedor, ContactoProveedor, ArticuloProveedor

for model in [Proveedor, ContactoProveedor, ArticuloProveedor]:
    admin.site.register(model, MasterAdmin)

from django.contrib import admin
from apps.core.admin import LedgerAdmin
from .models import OrdenCompra, DetalleOrdenCompra

for model in [OrdenCompra, DetalleOrdenCompra]:
    admin.site.register(model, LedgerAdmin)

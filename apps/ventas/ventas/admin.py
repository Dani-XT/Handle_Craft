from django.contrib import admin
from apps.core.admin import LedgerAdmin
from .models import Venta, DetalleVenta

for model in [Venta, DetalleVenta]:
    admin.site.register(model, LedgerAdmin)

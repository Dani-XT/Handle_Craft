from django.contrib import admin
from apps.core.admin import LedgerAdmin
from .models import RecepcionCompra, DetalleRecepcion

for model in [RecepcionCompra, DetalleRecepcion]:
    admin.site.register(model, LedgerAdmin)

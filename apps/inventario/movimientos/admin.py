from django.contrib import admin
from apps.core.admin import LedgerAdmin
from .models import Existencia, ReservaInventario, OperacionInventario, DetalleOperacion, MovimientoStock

for model in [Existencia, ReservaInventario, OperacionInventario, DetalleOperacion, MovimientoStock]:
    admin.site.register(model, LedgerAdmin)

from django.contrib import admin
from apps.core.admin import LedgerAdmin
from .models import Pedido, DetallePedido, HistorialEstadoPedido

for model in [Pedido, DetallePedido, HistorialEstadoPedido]:
    admin.site.register(model, LedgerAdmin)

from django.contrib import admin
from apps.core.admin import LedgerAdmin
from .models import Despacho, DetalleDespacho

for model in [Despacho, DetalleDespacho]:
    admin.site.register(model, LedgerAdmin)

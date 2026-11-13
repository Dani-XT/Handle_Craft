from django.contrib import admin
from apps.core.admin import LedgerAdmin
from .models import Pago, AplicacionPago, Reembolso

for model in [Pago, AplicacionPago, Reembolso]:
    admin.site.register(model, LedgerAdmin)

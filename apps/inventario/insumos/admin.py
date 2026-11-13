from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import Insumo, Lote, UnidadSerializada

for model in [Insumo, Lote, UnidadSerializada]:
    admin.site.register(model, MasterAdmin)

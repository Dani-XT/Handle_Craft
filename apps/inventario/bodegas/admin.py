from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import Bodega, Ubicacion

for model in [Bodega, Ubicacion]:
    admin.site.register(model, MasterAdmin)

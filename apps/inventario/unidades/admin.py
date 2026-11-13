from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import UnidadMedida

for model in [UnidadMedida]:
    admin.site.register(model, MasterAdmin)

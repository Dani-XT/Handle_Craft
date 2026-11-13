from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import Categoria

for model in [Categoria]:
    admin.site.register(model, MasterAdmin)

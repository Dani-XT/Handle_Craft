from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import Cliente, DireccionCliente, ContactoCliente

for model in [Cliente, DireccionCliente, ContactoCliente]:
    admin.site.register(model, MasterAdmin)

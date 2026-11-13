from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import ListaPrecio, PrecioArticulo
from .services import guardar_precio

admin.site.register(ListaPrecio, MasterAdmin)

@admin.register(PrecioArticulo)
class PrecioArticuloAdmin(MasterAdmin):
    def save_model(self, request, obj, form, change):
        guardar_precio(obj, request.user)

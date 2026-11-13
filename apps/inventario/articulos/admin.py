from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import Articulo

@admin.register(Articulo)
class ArticuloAdmin(MasterAdmin):
    list_display = ("sku", "nombre", "categoria", "seguimiento", "unidad_medida", "es_vendible")
    list_filter = ("seguimiento", "es_vendible", "categoria")
    search_fields = ("sku", "nombre")

from .models import PresentacionArticulo
admin.site.register(PresentacionArticulo, MasterAdmin)

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from apps.core.admin import MasterAdmin
from .models import Producto, VarianteProducto, ImagenProducto, TipoProducto
from .services import publicar_producto


@admin.register(Producto)
class ProductoAdmin(MasterAdmin):
    readonly_fields = MasterAdmin.readonly_fields + ("publicado",)
    actions = MasterAdmin.actions + ["publicar", "retirar"]
    list_display = ("nombre", "categoria", "publicado")
    prepopulated_fields = {"slug": ("nombre",)}

    @admin.action(description="Publicar productos", permissions=["change"])
    def publicar(self, request, queryset):
        for producto in queryset:
            try:
                publicar_producto(producto.pk, request.user)
            except ValidationError as error:
                self.message_user(request, str(error), level=messages.ERROR)

    @admin.action(description="Retirar del catálogo público", permissions=["change"])
    def retirar(self, request, queryset):
        for producto in queryset:
            producto.publicado = False
            producto.updated_by = request.user
            producto.save(update_fields=["publicado", "updated_by", "updated_at"])


for model in [VarianteProducto, ImagenProducto, TipoProducto]:
    admin.site.register(model, MasterAdmin)

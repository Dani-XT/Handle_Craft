from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Articulo


class MasterAdmin(admin.ModelAdmin):
    actions = ["archivar"]
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by", "archived_at", "archived_by")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Archivar registros seleccionados", permissions=["change"])
    def archivar(self, request, queryset):
        for obj in queryset:
            try:
                obj.archive(request.user)
            except ValidationError as error:
                self.message_user(request, str(error), level=messages.ERROR)


class LedgerAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Articulo)
class ArticuloAdmin(MasterAdmin):
    list_display = ("sku", "nombre", "categoria", "seguimiento", "unidad_medida", "es_vendible")
    list_filter = ("seguimiento", "es_vendible", "categoria")
    search_fields = ("sku", "nombre")

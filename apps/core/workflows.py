from django.core.exceptions import ValidationError
from django.utils import timezone


def exigir_borrador(documento):
    if documento.estado != "borrador" or documento.is_archived:
        raise ValidationError("Se requiere un documento activo en borrador.")


def marcar_confirmado(documento, actor=None):
    documento.estado = "confirmada"
    documento.confirmed_at = timezone.now()
    documento.updated_by = actor
    documento.save(workflow_write=True)
    return documento


def copiar_linea(origen):
    campos = ("articulo_id", "sku", "descripcion", "cantidad", "precio_unitario", "costo_personalizacion", "descuento", "tasa_impuesto", "especificaciones")
    return {campo: getattr(origen, campo) for campo in campos}

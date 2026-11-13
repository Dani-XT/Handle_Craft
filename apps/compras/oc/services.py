from django.core.exceptions import ValidationError
from django.db import transaction
from apps.core.workflows import exigir_borrador, marcar_confirmado
from .models import OrdenCompra


@transaction.atomic
def confirmar_orden(orden_id, actor=None):
    orden = OrdenCompra.objects.select_for_update().get(pk=orden_id)
    if orden.estado == "confirmada":
        return orden
    exigir_borrador(orden)
    detalles = list(orden.detalles.filter(archived_at__isnull=True))
    if orden.proveedor.is_archived or not detalles:
        raise ValidationError("Se necesita proveedor activo y al menos un detalle.")
    for detalle in detalles:
        detalle.full_clean()
        if detalle.articulo.is_archived or not detalle.articulo.es_comprable:
            raise ValidationError("El artículo debe estar activo y ser comprable.")
    return marcar_confirmado(orden, actor)

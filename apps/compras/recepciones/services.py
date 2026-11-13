from collections import defaultdict
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from apps.core.workflows import exigir_borrador, marcar_confirmado
from apps.compras.oc.models import OrdenCompra
from apps.inventario.movimientos.models import OperacionInventario
from apps.inventario.movimientos.services import agregar_detalle, confirmar_operacion, validar_cantidad
from .models import RecepcionCompra, DetalleRecepcion


@transaction.atomic
def confirmar_recepcion(recepcion_id, actor=None):
    orden_id = RecepcionCompra.objects.values_list("orden_id", flat=True).get(pk=recepcion_id)
    orden = OrdenCompra.objects.select_for_update().get(pk=orden_id)
    recepcion = RecepcionCompra.objects.select_for_update().get(pk=recepcion_id)
    if recepcion.estado == "confirmada":
        return recepcion
    exigir_borrador(recepcion)
    if orden.estado != "confirmada":
        raise ValidationError("La orden debe estar confirmada.")
    detalles = list(recepcion.detalles.filter(archived_at__isnull=True))
    if not detalles:
        raise ValidationError("La recepción no tiene detalles.")
    cantidades = defaultdict(Decimal)
    for detalle in detalles:
        detalle.full_clean()
        for cantidad in (detalle.cantidad_aceptada, detalle.cantidad_rechazada):
            if cantidad:
                validar_cantidad(cantidad, detalle.detalle_orden.articulo)
        cantidades[detalle.detalle_orden_id] += detalle.cantidad_aceptada
    for linea in orden.detalles.filter(pk__in=cantidades):
        recibida = DetalleRecepcion.objects.filter(detalle_orden=linea, recepcion__estado="confirmada").aggregate(total=Sum("cantidad_aceptada"))["total"] or Decimal("0")
        if linea.is_archived or recibida + cantidades[linea.pk] > linea.cantidad:
            raise ValidationError("La recepción excede la cantidad comprada.")
    aceptados = [detalle for detalle in detalles if detalle.cantidad_aceptada > 0]
    if aceptados:
        op = OperacionInventario.objects.create(tipo="entrada", referencia=str(recepcion.codigo), motivo="Recepción de orden de compra", created_by=actor, updated_by=actor)
        for detalle in aceptados:
            agregar_detalle(operacion_id=op.pk, destino=detalle.destino, cantidad=detalle.cantidad_aceptada, actor=actor)
        confirmar_operacion(op.pk, actor)
        recepcion.operacion = op
    return marcar_confirmado(recepcion, actor)

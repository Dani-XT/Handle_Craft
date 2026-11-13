from collections import defaultdict
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from apps.core.workflows import exigir_borrador, marcar_confirmado
from apps.ventas.pedidos.models import Pedido
from apps.inventario.movimientos.models import OperacionInventario
from apps.inventario.movimientos.services import agregar_detalle, confirmar_operacion
from .models import Despacho, DetalleDespacho


@transaction.atomic
def confirmar_despacho(despacho_id, actor=None):
    pedido_id = Despacho.objects.values_list("pedido_id", flat=True).get(pk=despacho_id)
    pedido = Pedido.objects.select_for_update().get(pk=pedido_id)
    despacho = Despacho.objects.select_for_update().get(pk=despacho_id)
    if despacho.estado == "confirmada":
        return despacho
    exigir_borrador(despacho)
    if pedido.estado != "confirmada":
        raise ValidationError("El pedido debe estar confirmado.")
    detalles = list(despacho.detalles.filter(archived_at__isnull=True))
    if not detalles:
        raise ValidationError("El despacho no tiene detalles.")
    cantidades = defaultdict(Decimal)
    for detalle in detalles:
        detalle.full_clean()
        cantidades[detalle.detalle_pedido_id] += detalle.cantidad
    for linea in pedido.detalles.filter(pk__in=cantidades):
        entregada = DetalleDespacho.objects.filter(detalle_pedido=linea, despacho__estado="confirmada").aggregate(total=Sum("cantidad"))["total"] or Decimal("0")
        if linea.is_archived or entregada + cantidades[linea.pk] > linea.cantidad:
            raise ValidationError("El despacho excede lo pedido.")
    op = OperacionInventario.objects.create(tipo="salida", referencia=str(despacho.codigo), motivo="Despacho de pedido", created_by=actor, updated_by=actor)
    for detalle in detalles:
        agregar_detalle(operacion_id=op.pk, origen=detalle.reserva.existencia, cantidad=detalle.cantidad, reserva=detalle.reserva, actor=actor)
    confirmar_operacion(op.pk, actor)
    despacho.operacion = op
    return marcar_confirmado(despacho, actor)

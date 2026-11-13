from django.core.exceptions import ValidationError
from django.db import transaction
from apps.core.workflows import copiar_linea, marcar_confirmado
from apps.ventas.pedidos.models import Pedido
from .models import Venta, DetalleVenta


@transaction.atomic
def registrar_venta(pedido_id, actor=None):
    pedido = Pedido.objects.select_for_update().get(pk=pedido_id)
    existente = Venta.objects.filter(pedido=pedido).first()
    if existente:
        return existente
    if pedido.estado != "confirmada":
        raise ValidationError("El pedido debe estar confirmado.")
    venta = Venta.objects.create(pedido=pedido, cliente=pedido.cliente, nombre_cliente=pedido.nombre_cliente, moneda=pedido.moneda, created_by=actor, updated_by=actor)
    for detalle in pedido.detalles.filter(archived_at__isnull=True):
        DetalleVenta.objects.create(venta=venta, detalle_pedido=detalle, created_by=actor, updated_by=actor, **copiar_linea(detalle))
    return marcar_confirmado(venta, actor)

from django.db import transaction
from django.core.exceptions import ValidationError
from apps.core.workflows import exigir_borrador, marcar_confirmado
from apps.catalogo.cotizaciones.models import Cotizacion
from .models import Pedido, DetallePedido, HistorialEstadoPedido


@transaction.atomic
def confirmar_pedido(pedido_id, actor=None):
    pedido = Pedido.objects.select_for_update().get(pk=pedido_id)
    if pedido.estado == "confirmada":
        return pedido
    exigir_borrador(pedido)
    detalles = list(pedido.detalles.filter(archived_at__isnull=True))
    if pedido.cliente.is_archived or not detalles:
        raise ValidationError("Se necesita cliente activo y al menos un detalle.")
    for detalle in detalles:
        detalle.full_clean()
        if detalle.detalle_cotizacion_id and detalle.detalle_cotizacion.personalizaciones.filter(archived_at__isnull=True, aprobacion__isnull=True).exists():
            raise ValidationError("Hay diseños personalizados pendientes de aprobación.")
        if detalle.articulo.is_archived or not detalle.articulo.es_vendible:
            raise ValidationError("Todos los artículos deben estar activos y ser vendibles.")
    marcar_confirmado(pedido, actor)
    HistorialEstadoPedido.objects.create(pedido=pedido, anterior="borrador", nuevo="confirmada", created_by=actor)
    return pedido


@transaction.atomic
def crear_desde_cotizacion(cotizacion_id, actor=None):
    cotizacion = Cotizacion.objects.select_for_update().get(pk=cotizacion_id)
    existente = Pedido.objects.filter(cotizacion=cotizacion).first()
    if existente:
        return existente
    if cotizacion.estado != "aceptada" or cotizacion.is_archived or not cotizacion.cliente_id:
        raise ValidationError("Se requiere una cotización aceptada y vinculada a un cliente.")
    pedido = Pedido.objects.create(cliente=cotizacion.cliente, cotizacion=cotizacion, moneda=cotizacion.moneda, nombre_cliente=cotizacion.nombre_cliente, direccion_entrega=cotizacion.direccion_cliente, created_by=actor, updated_by=actor)
    for detalle in cotizacion.detalles.filter(archived_at__isnull=True):
        campos = {campo: getattr(detalle, campo) for campo in ("sku", "descripcion", "cantidad", "precio_unitario", "costo_personalizacion", "descuento", "tasa_impuesto", "especificaciones")}
        DetallePedido.objects.create(pedido=pedido, detalle_cotizacion=detalle, articulo=detalle.variante.articulo, created_by=actor, updated_by=actor, **campos)
    return confirmar_pedido(pedido.pk, actor)

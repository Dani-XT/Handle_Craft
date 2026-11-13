from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from apps.core.workflows import exigir_borrador, marcar_confirmado
from apps.ventas.pedidos.models import Pedido
from .models import Pago, AplicacionPago, Reembolso


def importe_valido(importe):
    importe = Decimal(str(importe))
    if not importe.is_finite() or importe <= 0 or importe != importe.quantize(Decimal("0.01")):
        raise ValidationError("Importe positivo con máximo dos decimales requerido.")
    return importe


def pagado_pedido(pedido_id):
    aplicado = AplicacionPago.objects.filter(pedido_id=pedido_id).aggregate(total=Sum("importe"))["total"] or Decimal("0")
    devuelto = Reembolso.objects.filter(aplicacion__pedido_id=pedido_id).aggregate(total=Sum("importe"))["total"] or Decimal("0")
    return aplicado - devuelto


@transaction.atomic
def confirmar_pago(pago_id, actor=None):
    pago = Pago.objects.select_for_update().get(pk=pago_id)
    if pago.estado == "confirmada":
        return pago
    exigir_borrador(pago)
    if pago.cliente.is_archived:
        raise ValidationError("El cliente está archivado.")
    return marcar_confirmado(pago, actor)


@transaction.atomic
def aplicar_pago(*, pago_id, pedido_id, importe, clave, actor=None):
    pedido = Pedido.objects.select_for_update().get(pk=pedido_id)
    pago = Pago.objects.select_for_update().get(pk=pago_id)
    importe = importe_valido(importe)
    existente = AplicacionPago.objects.filter(clave=clave).first()
    if existente:
        if (existente.pago_id, existente.pedido_id, existente.importe) != (pago_id, pedido_id, importe):
            raise ValidationError("La clave ya fue usada con otros datos.")
        return existente
    if pedido.estado != "confirmada" or pago.estado != "confirmada":
        raise ValidationError("El pedido y el pago deben estar confirmados.")
    aplicado = pago.aplicaciones.aggregate(total=Sum("importe"))["total"] or Decimal("0")
    if aplicado + importe > pago.importe or pagado_pedido(pedido_id) + importe > pedido.total:
        raise ValidationError("La aplicación excede el pago disponible o el saldo del pedido.")
    return AplicacionPago.objects.create(pago=pago, pedido=pedido, importe=importe, clave=clave, created_by=actor, updated_by=actor)


@transaction.atomic
def reembolsar(*, aplicacion_id, importe, motivo, clave, actor=None):
    datos = AplicacionPago.objects.values("pedido_id", "pago_id").get(pk=aplicacion_id)
    Pedido.objects.select_for_update().get(pk=datos["pedido_id"])
    Pago.objects.select_for_update().get(pk=datos["pago_id"])
    aplicacion = AplicacionPago.objects.select_for_update().get(pk=aplicacion_id)
    importe = importe_valido(importe)
    existente = Reembolso.objects.filter(clave=clave).first()
    if existente:
        if existente.aplicacion_id != aplicacion_id or existente.importe != importe:
            raise ValidationError("La clave ya fue utilizada con otros datos.")
        return existente
    devuelto = aplicacion.reembolsos.aggregate(total=Sum("importe"))["total"] or Decimal("0")
    if devuelto + importe > aplicacion.importe:
        raise ValidationError("El reembolso supera lo aplicado.")
    return Reembolso.objects.create(aplicacion=aplicacion, importe=importe, motivo=motivo, clave=clave, created_by=actor, updated_by=actor)

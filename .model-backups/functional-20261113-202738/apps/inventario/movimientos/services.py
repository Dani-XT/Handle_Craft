from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from apps.core.models import Articulo
from .models import (Existencia, ReservaInventario, OperacionInventario,
                     DetalleOperacion, MovimientoStock)
from .selectors import existencias_despachables


def validar_cantidad(value, articulo):
    try:
        value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError("Cantidad inválida.")
    if not value.is_finite() or value <= 0 or value.as_tuple().exponent < -3:
        raise ValidationError("La cantidad debe ser positiva y tener como máximo tres decimales.")
    if articulo.unidad_medida == "un" and value % 1:
        raise ValidationError("Las unidades no admiten fracciones.")
    return value


def bloquear_articulos(ids):
    # Orden común para operaciones y reservas: artículo, existencia, reserva.
    return list(Articulo.objects.select_for_update().filter(pk__in=ids).order_by("pk"))


@transaction.atomic
def abrir_existencia(*, articulo, ubicacion, lote=None, unidad_serializada=None, actor=None):
    bloquear_articulos([articulo.pk])
    datos = dict(articulo=articulo, ubicacion=ubicacion, lote=lote, unidad_serializada=unidad_serializada)
    existente = Existencia.objects.filter(**datos).first()
    if existente:
        return existente
    existencia = Existencia(**datos, created_by=actor, updated_by=actor)
    existencia.full_clean()
    existencia.save()
    return existencia


@transaction.atomic
def agregar_detalle(*, operacion_id, cantidad, origen=None, destino=None, reserva=None, actor=None):
    operacion = OperacionInventario.objects.select_for_update().get(pk=operacion_id)
    if operacion.estado != "borrador" or operacion.is_archived:
        raise ValidationError("Solo se agregan líneas a operaciones en borrador.")
    detalle = DetalleOperacion(operacion=operacion, cantidad=cantidad, origen=origen,
                               destino=destino, reserva=reserva, created_by=actor, updated_by=actor)
    detalle.full_clean()
    detalle.save()
    return detalle


@transaction.atomic
def confirmar_operacion(operacion_id, actor=None):
    op = OperacionInventario.objects.select_for_update().get(pk=operacion_id)
    if op.estado == "confirmada":
        return op
    if op.estado != "borrador" or op.is_archived:
        raise ValidationError("La operación no se puede confirmar.")
    op.full_clean()
    if op.corrige_id and (op.corrige_id == op.pk or op.corrige.estado != "confirmada"):
        raise ValidationError("Solo se pueden corregir otras operaciones confirmadas.")
    detalles = list(op.detalles.filter(archived_at__isnull=True).order_by("pk"))
    if not detalles:
        raise ValidationError("La operación necesita al menos una línea.")
    ids = {pk for d in detalles for pk in (d.origen_id, d.destino_id) if pk}
    bloquear_articulos(Existencia.objects.filter(pk__in=ids).values_list("articulo_id", flat=True))
    saldos = {e.pk: e for e in Existencia.objects.select_for_update().filter(pk__in=ids).order_by("pk")}
    entrada = op.tipo in ("entrada", "ajuste_entrada")
    salida = op.tipo in ("salida", "ajuste_salida")
    for d in detalles:
        d.full_clean()
        if entrada and (d.origen_id or not d.destino_id):
            raise ValidationError("Una entrada requiere solo destino.")
        if salida and (not d.origen_id or d.destino_id):
            raise ValidationError("Una salida requiere solo origen.")
        if op.tipo == "transferencia":
            if not d.origen_id or not d.destino_id:
                raise ValidationError("La transferencia requiere origen y destino.")
            a, b = saldos[d.origen_id], saldos[d.destino_id]
            if (a.articulo_id, a.lote_id, a.unidad_serializada_id) != (b.articulo_id, b.lote_id, b.unidad_serializada_id):
                raise ValidationError("La transferencia debe conservar artículo, lote y serie.")
        reserva = None
        if d.reserva_id:
            reserva = ReservaInventario.objects.select_for_update().get(pk=d.reserva_id)
            if op.tipo != "salida" or reserva.existencia_id != d.origen_id or reserva.pendiente < d.cantidad:
                raise ValidationError("La reserva no corresponde o su saldo es insuficiente.")
        for pk, signo in ((d.origen_id, -1), (d.destino_id, 1)):
            if pk is None:
                continue
            e = saldos[pk]
            cantidad = validar_cantidad(d.cantidad, e.articulo)
            e.full_clean()
            if e.is_archived or e.articulo.is_archived or e.ubicacion.is_archived or e.ubicacion.bodega.is_archived or not e.ubicacion.bodega.activa:
                raise ValidationError("El artículo y la ubicación deben estar activos.")
            if (e.lote_id and e.lote.is_archived) or (e.unidad_serializada_id and e.unidad_serializada.is_archived):
                raise ValidationError("La trazabilidad está archivada.")
            if signo < 0:
                if op.tipo == "salida" and not existencias_despachables().filter(pk=e.pk).exists():
                    raise ValidationError("La existencia está bloqueada, en cuarentena o vencida.")
                disponible = e.disponible + (reserva.pendiente if reserva else Decimal("0"))
                if cantidad > disponible:
                    raise ValidationError("Stock disponible insuficiente.")
            e.cantidad += signo * cantidad
            e.updated_by = actor
            e.full_clean()
            e.save(stock_write=True, update_fields=["cantidad", "updated_by", "updated_at"])
            MovimientoStock.objects.create(detalle=d, existencia=e, variacion=signo*cantidad, created_by=actor)
        if reserva:
            reserva.despachada += d.cantidad
            reserva.updated_by = actor
            reserva.full_clean()
            reserva.save(update_fields=["despachada", "updated_by", "updated_at"])
    op.estado = "confirmada"
    op.confirmed_at = timezone.now()
    op.confirmed_by = actor
    op.updated_by = actor
    op.full_clean()
    op.save(workflow_write=True, update_fields=["estado", "confirmed_at", "confirmed_by", "updated_by", "updated_at"])
    return op


@transaction.atomic
def reservar(*, existencia_id, cantidad, referencia, actor=None):
    articulo_id = Existencia.objects.values_list("articulo_id", flat=True).get(pk=existencia_id)
    bloquear_articulos([articulo_id])
    e = Existencia.objects.select_for_update().get(pk=existencia_id)
    cantidad = validar_cantidad(cantidad, e.articulo)
    if not existencias_despachables().filter(pk=e.pk).exists() or cantidad > e.disponible:
        raise ValidationError("Stock disponible insuficiente o no despachable.")
    reserva = ReservaInventario(existencia=e, cantidad=cantidad, referencia=referencia, created_by=actor, updated_by=actor)
    reserva.full_clean()
    reserva.save()
    return reserva


@transaction.atomic
def liberar_reserva(reserva_id, cantidad, actor=None):
    datos = ReservaInventario.objects.values("existencia_id", "existencia__articulo_id").get(pk=reserva_id)
    bloquear_articulos([datos["existencia__articulo_id"]])
    e = Existencia.objects.select_for_update().get(pk=datos["existencia_id"])
    reserva = ReservaInventario.objects.select_for_update().get(pk=reserva_id)
    cantidad = validar_cantidad(cantidad, e.articulo)
    if cantidad > reserva.pendiente:
        raise ValidationError("No se puede liberar más de lo pendiente.")
    reserva.liberada += cantidad
    reserva.updated_by = actor
    reserva.full_clean()
    reserva.save(update_fields=["liberada", "updated_by", "updated_at"])
    return reserva


@transaction.atomic
def cancelar_operacion(operacion_id, actor=None):
    op = OperacionInventario.objects.select_for_update().get(pk=operacion_id)
    if op.estado != "borrador":
        raise ValidationError("Solo se cancelan borradores. Un movimiento confirmado se compensa con otra operación.")
    op.estado = "cancelada"
    op.updated_by = actor
    op.save(workflow_write=True, update_fields=["estado", "updated_by", "updated_at"])
    return op

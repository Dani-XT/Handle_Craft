import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from apps.core.models import ArchiveQuerySet, BaseModel


class Existencia(BaseModel):
    articulo = models.ForeignKey("apps_core.Articulo", on_delete=models.PROTECT, related_name="existencias")
    ubicacion = models.ForeignKey("bodegas.Ubicacion", on_delete=models.PROTECT, related_name="existencias")
    lote = models.ForeignKey("insumos.Lote", on_delete=models.PROTECT, null=True, blank=True)
    unidad_serializada = models.ForeignKey("insumos.UnidadSerializada", on_delete=models.PROTECT, null=True, blank=True, related_name="existencias")
    cantidad = models.DecimalField(max_digits=16, decimal_places=3, default=Decimal("0"), editable=False)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(cantidad__gte=0), name="existencia_no_negativa"),
            models.CheckConstraint(condition=models.Q(unidad_serializada__isnull=True) | models.Q(cantidad__in=[0, 1]), name="existencia_serie_cero_uno"),
            models.CheckConstraint(condition=models.Q(unidad_serializada__isnull=True) | models.Q(lote__isnull=True), name="existencia_lote_o_serie"),
            models.UniqueConstraint(fields=["articulo", "ubicacion"], condition=models.Q(lote__isnull=True, unidad_serializada__isnull=True), name="existencia_cantidad_unica"),
            models.UniqueConstraint(fields=["articulo", "ubicacion", "lote"], condition=models.Q(lote__isnull=False, unidad_serializada__isnull=True), name="existencia_lote_unica"),
            models.UniqueConstraint(fields=["ubicacion", "unidad_serializada"], condition=models.Q(unidad_serializada__isnull=False), name="existencia_serie_ubic_unica"),
            models.UniqueConstraint(fields=["unidad_serializada"], condition=models.Q(unidad_serializada__isnull=False, cantidad__gt=0), name="serie_una_ubicacion_con_stock"),
        ]

    def clean(self):
        super().clean()
        if not self.articulo_id:
            return
        modo = self.articulo.seguimiento
        if modo == "cantidad" and (self.lote_id or self.unidad_serializada_id):
            raise ValidationError("El control por cantidad no utiliza lote ni serie.")
        if modo == "lote" and (not self.lote_id or self.unidad_serializada_id):
            raise ValidationError("El control por lote requiere exclusivamente un lote.")
        if modo == "serie" and (not self.unidad_serializada_id or self.lote_id):
            raise ValidationError("El control por serie requiere una unidad serializada; su lote se consulta en esa unidad.")
        if self.lote_id and self.lote.articulo_id != self.articulo_id:
            raise ValidationError({"lote": "El lote no corresponde al artículo."})
        if self.unidad_serializada_id and self.unidad_serializada.articulo_id != self.articulo_id:
            raise ValidationError({"unidad_serializada": "La serie no corresponde al artículo."})
        if self.cantidad is not None and self.articulo.unidad_medida_id == "un" and Decimal(self.cantidad) % 1:
            raise ValidationError({"cantidad": "Las unidades deben ser enteras."})

    def save(self, *args, stock_write=False, **kwargs):
        if self.pk:
            old = type(self).objects.get(pk=self.pk)
            for field in ("articulo_id", "ubicacion_id", "lote_id", "unidad_serializada_id"):
                if getattr(old, field) != getattr(self, field):
                    raise ValidationError("La identidad de una existencia no se modifica; cree otra existencia.")
            if old.cantidad != self.cantidad and not stock_write:
                raise ValidationError("El saldo solo se modifica mediante el servicio de movimientos.")
        elif self.cantidad != 0:
            raise ValidationError("Las existencias se crean en cero; registre una entrada.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def validate_archive(self):
        raise ValidationError("Las existencias se conservan para mantener la trazabilidad.")

    @property
    def reservada(self):
        return self.reservas.aggregate(total=models.Sum(models.F("cantidad") - models.F("despachada") - models.F("liberada")))["total"] or Decimal("0")

    @property
    def disponible(self):
        return self.cantidad - self.reservada

    def __str__(self):
        return f"{self.articulo.sku} / {self.ubicacion}"


class ReservaInventario(BaseModel):
    detalle_pedido = models.ForeignKey("pedidos.DetallePedido", on_delete=models.PROTECT, null=True, blank=True, related_name="reservas")
    existencia = models.ForeignKey(Existencia, on_delete=models.PROTECT, related_name="reservas")
    referencia = models.CharField(max_length=100, help_text="Identificador del pedido o compromiso.")
    cantidad = models.DecimalField(max_digits=16, decimal_places=3)
    despachada = models.DecimalField(max_digits=16, decimal_places=3, default=Decimal("0"), editable=False)
    liberada = models.DecimalField(max_digits=16, decimal_places=3, default=Decimal("0"), editable=False)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(cantidad__gt=0, despachada__gte=0, liberada__gte=0, cantidad__gte=models.F("despachada") + models.F("liberada")), name="reserva_cantidades_validas")]

    def validate_archive(self):
        raise ValidationError("Las reservas se liberan mediante el servicio, no se archivan.")

    @property
    def pendiente(self):
        return self.cantidad - self.despachada - self.liberada


class OperacionInventario(BaseModel):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"
        TRANSFERENCIA = "transferencia", "Transferencia"
        AJUSTE_ENTRADA = "ajuste_entrada", "Ajuste positivo"
        AJUSTE_SALIDA = "ajuste_salida", "Ajuste negativo"

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        CONFIRMADA = "confirmada", "Confirmada"
        CANCELADA = "cancelada", "Cancelada"

    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    tipo = models.CharField(max_length=16, choices=Tipo.choices)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.BORRADOR, editable=False)
    referencia = models.CharField(max_length=100, blank=True)
    motivo = models.TextField()
    corrige = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="correcciones")
    confirmed_at = models.DateTimeField(null=True, blank=True, editable=False)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, editable=False, related_name="+")

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(tipo__in=["entrada", "salida", "transferencia", "ajuste_entrada", "ajuste_salida"]), name="operacion_tipo_valido"),
            models.CheckConstraint(condition=models.Q(estado__in=["borrador", "confirmada", "cancelada"]), name="operacion_estado_valido"),
            models.CheckConstraint(condition=models.Q(estado="confirmada", confirmed_at__isnull=False) | models.Q(estado__in=["borrador", "cancelada"], confirmed_at__isnull=True), name="operacion_confirmacion_coherente"),
        ]

    def save(self, *args, workflow_write=False, **kwargs):
        if self.estado != "borrador" and not workflow_write:
            raise ValidationError("Use confirmar_operacion o cancelar_operacion para cambiar de estado.")
        if self.pk and type(self).objects.filter(pk=self.pk).exclude(estado="borrador").exists():
            raise ValidationError("Las operaciones confirmadas o canceladas no son editables.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def validate_archive(self):
        raise ValidationError("Cancele el borrador o registre una operación compensatoria.")

    def __str__(self):
        return str(self.codigo)


class DetalleOperacion(BaseModel):
    operacion = models.ForeignKey(OperacionInventario, on_delete=models.PROTECT, related_name="detalles")
    origen = models.ForeignKey(Existencia, on_delete=models.PROTECT, null=True, blank=True, related_name="detalles_salida")
    destino = models.ForeignKey(Existencia, on_delete=models.PROTECT, null=True, blank=True, related_name="detalles_entrada")
    cantidad = models.DecimalField(max_digits=16, decimal_places=3)
    reserva = models.ForeignKey(ReservaInventario, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(cantidad__gt=0), name="detalle_mov_cantidad_positiva"),
            models.CheckConstraint(condition=models.Q(origen__isnull=False) | models.Q(destino__isnull=False), name="detalle_mov_tiene_ubicacion"),
            models.CheckConstraint(condition=~models.Q(origen=models.F("destino")), name="detalle_mov_distinto_destino"),
        ]

    def save(self, *args, **kwargs):
        from django.db import transaction
        with transaction.atomic():
            op = OperacionInventario.objects.select_for_update().get(pk=self.operacion_id)
            if op.estado != "borrador":
                raise ValidationError("No se pueden modificar líneas de una operación cerrada.")
            if self.pk and type(self).objects.filter(pk=self.pk).exclude(operacion_id=self.operacion_id).exists():
                raise ValidationError("Una línea no se puede trasladar a otra operación.")
            self.full_clean()
            return super().save(*args, **kwargs)

    def validate_archive(self):
        if self.operacion.estado != "borrador":
            raise ValidationError("No se pueden archivar líneas de operaciones confirmadas.")


class MovimientoStock(models.Model):
    objects = ArchiveQuerySet.as_manager()
    detalle = models.ForeignKey(DetalleOperacion, on_delete=models.PROTECT, related_name="movimientos")
    existencia = models.ForeignKey(Existencia, on_delete=models.PROTECT, related_name="movimientos")
    variacion = models.DecimalField(max_digits=16, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="+")

    class Meta:
        default_permissions = ("view",)
        constraints = [
            models.CheckConstraint(condition=~models.Q(variacion=0), name="movimiento_no_cero"),
            models.UniqueConstraint(fields=["detalle", "existencia"], name="movimiento_detalle_exist_unico"),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("El registro de movimientos es inmutable.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Los movimientos se compensan, no se eliminan.")

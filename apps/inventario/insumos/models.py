from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import BaseModel


class Insumo(BaseModel):
    """Información interna adicional; la identidad y el stock pertenecen a Articulo."""
    articulo = models.OneToOneField("apps_core.Articulo", on_delete=models.PROTECT, related_name="insumo")
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    instrucciones_almacenamiento = models.TextField(blank=True)

    def __str__(self):
        return str(self.articulo)


class Lote(BaseModel):
    articulo = models.ForeignKey("apps_core.Articulo", on_delete=models.PROTECT, related_name="lotes")
    codigo = models.CharField(max_length=80)
    fecha_fabricacion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["articulo", "codigo"], name="lote_codigo_articulo_unico"),
            models.CheckConstraint(condition=models.Q(fecha_fabricacion__isnull=True) | models.Q(fecha_vencimiento__isnull=True) | models.Q(fecha_vencimiento__gte=models.F("fecha_fabricacion")), name="lote_fechas_validas"),
        ]

    def clean(self):
        super().clean()
        if self.pk and type(self).objects.filter(pk=self.pk).exclude(articulo_id=self.articulo_id).exists():
            raise ValidationError("Un lote no puede cambiar de artículo.")
        if self.articulo_id and self.articulo.seguimiento == "cantidad":
            raise ValidationError({"articulo": "Este artículo no se controla por lote o serie."})

    def validate_archive(self):
        from apps.inventario.movimientos.models import Existencia
        if Existencia.objects.filter(models.Q(lote=self) | models.Q(unidad_serializada__lote=self), cantidad__gt=0).exists():
            raise ValidationError("El lote todavía tiene stock físico.")

    def __str__(self):
        return f"{self.articulo.sku} / {self.codigo}"


class UnidadSerializada(BaseModel):
    articulo = models.ForeignKey("apps_core.Articulo", on_delete=models.PROTECT, related_name="series")
    serial = models.CharField(max_length=100)
    codigo_interno = models.CharField(max_length=100, unique=True)
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, null=True, blank=True, related_name="series")
    observaciones = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["articulo", "serial"], name="serial_unico_por_articulo")]

    def clean(self):
        super().clean()
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).first()
            if old and (old.articulo_id, old.serial, old.codigo_interno, old.lote_id) != (self.articulo_id, self.serial, self.codigo_interno, self.lote_id):
                raise ValidationError("La identidad y el lote de una unidad serializada no se modifican.")
        if self.articulo_id and not self.articulo.requiere_serial:
            raise ValidationError({"articulo": "El artículo debe usar seguimiento por serie."})
        if self.lote_id and self.lote.articulo_id != self.articulo_id:
            raise ValidationError({"lote": "El lote pertenece a otro artículo."})

    def validate_archive(self):
        if self.existencias.filter(cantidad__gt=0).exists():
            raise ValidationError("La unidad serializada todavía está en inventario.")

    def __str__(self):
        return self.codigo_interno

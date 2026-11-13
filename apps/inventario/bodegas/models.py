from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class Bodega(BaseModel):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    direccion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    def validate_archive(self):
        if self.ubicaciones.filter(existencias__cantidad__gt=0).exists():
            raise ValidationError("La bodega todavía tiene stock físico.")

    class Meta:
        ordering = ["nombre", "pk"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Ubicacion(BaseModel):
    class Condicion(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        CUARENTENA = "cuarentena", "Cuarentena"
        BLOQUEADA = "bloqueada", "Bloqueada"

    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name="ubicaciones")
    codigo = models.CharField(max_length=40)
    nombre = models.CharField(max_length=100)
    condicion = models.CharField(max_length=12, choices=Condicion.choices, default=Condicion.DISPONIBLE)
    permite_despacho = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["bodega", "codigo"], name="ubicacion_codigo_bodega_unico"),
            models.CheckConstraint(condition=models.Q(condicion__in=["disponible", "cuarentena", "bloqueada"]), name="ubicacion_condicion_valida"),
        ]

    def validate_archive(self):
        if self.existencias.filter(cantidad__gt=0).exists():
            raise ValidationError("La ubicación todavía tiene stock físico.")

    def __str__(self):
        return f"{self.bodega.codigo} / {self.codigo}"

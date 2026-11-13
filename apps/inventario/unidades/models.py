from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class UnidadMedida(BaseModel):
    codigo = models.CharField(max_length=12, primary_key=True)
    nombre = models.CharField(max_length=80)
    simbolo = models.CharField(max_length=12)
    magnitud = models.CharField(max_length=12, choices=[("conteo", "Conteo"), ("masa", "Masa"), ("longitud", "Longitud"), ("volumen", "Volumen"), ("empaque", "Empaque")])
    decimales = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(decimales__lte=3), name="unidad_decimales_max_tres")]

    @property
    def permite_fracciones(self):
        return self.decimales > 0

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()
        old = type(self).objects.filter(pk=self.pk).first() if self.pk else None
        if old and (old.magnitud != self.magnitud or old.decimales != self.decimales) and self.articulos.exists():
            raise ValidationError("No cambie magnitud o precisión de una unidad ya utilizada por artículos.")

    def validate_archive(self):
        if self.articulos.filter(archived_at__isnull=True).exists():
            raise ValidationError("La unidad tiene artículos activos.")

from django.db import models, transaction
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class Diseno(BaseModel):
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="disenos")
    nombre = models.CharField(max_length=150)

    def clean(self):
        super().clean()
        if self.pk and self.versiones.exists() and type(self).objects.filter(pk=self.pk).exclude(cliente_id=self.cliente_id).exists():
            raise ValidationError("Un diseño versionado no puede cambiar de propietario.")


class VersionDiseno(BaseModel):
    diseno = models.ForeignKey(Diseno, on_delete=models.PROTECT, related_name="versiones")
    numero = models.PositiveIntegerField()
    archivo = models.FileField(upload_to="personalizaciones/disenos/%Y/%m/")
    observaciones = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["diseno", "numero"], name="diseno_version_unica"), models.CheckConstraint(condition=models.Q(numero__gt=0), name="diseno_version_positiva")]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Cree una versión nueva; los archivos versionados son inmutables.")
        return super().save(*args, **kwargs)

    def validate_archive(self):
        raise ValidationError("Las versiones se conservan como evidencia.")


class PersonalizacionDetalle(BaseModel):
    detalle_cotizacion = models.ForeignKey("cotizaciones.DetalleCotizacion", on_delete=models.PROTECT, related_name="personalizaciones")
    version = models.ForeignKey(VersionDiseno, on_delete=models.PROTECT, related_name="aplicaciones")
    posicion = models.CharField(max_length=80)
    ancho_mm = models.PositiveIntegerField()
    alto_mm = models.PositiveIntegerField()
    colores = models.JSONField(default=list)
    tecnica = models.CharField(max_length=80)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(ancho_mm__gt=0, alto_mm__gt=0), name="personalizacion_dimensiones_positivas")]

    def clean(self):
        super().clean()
        if self.version_id and self.detalle_cotizacion_id:
            if self.detalle_cotizacion.cotizacion.cliente_id != self.version.diseno.cliente_id:
                raise ValidationError("El diseño y la cotización deben pertenecer al mismo cliente.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                type(self).objects.select_for_update().get(pk=self.pk)
                if AprobacionDiseno.objects.filter(personalizacion_id=self.pk).exists():
                    raise ValidationError("Una personalización aprobada no se modifica.")
            return super().save(*args, **kwargs)


class AprobacionDiseno(BaseModel):
    personalizacion = models.OneToOneField(PersonalizacionDetalle, on_delete=models.PROTECT, related_name="aprobacion")
    comentario = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("La aprobación se conserva como evidencia.")
        return super().save(*args, **kwargs)

    def validate_archive(self):
        raise ValidationError("La aprobación no se archiva.")

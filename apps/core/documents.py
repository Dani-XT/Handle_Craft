import uuid
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import BaseModel


class DocumentoBase(BaseModel):
    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    estado = models.CharField(max_length=12, choices=[("borrador", "Borrador"), ("confirmada", "Confirmado"), ("cancelada", "Cancelado")], default="borrador", editable=False)
    fecha = models.DateField(default=timezone.localdate)
    confirmed_at = models.DateTimeField(null=True, blank=True, editable=False)
    observaciones = models.TextField(blank=True)

    class Meta:
        abstract = True
        constraints = [models.CheckConstraint(condition=models.Q(estado="borrador", confirmed_at__isnull=True) | models.Q(estado="cancelada", confirmed_at__isnull=True) | models.Q(estado="confirmada", confirmed_at__isnull=False), name="%(app_label)s_%(class)s_estado_fecha")]

    def save(self, *args, workflow_write=False, **kwargs):
        with transaction.atomic():
            old = type(self).objects.select_for_update().filter(pk=self.pk).first() if self.pk else None
            if not workflow_write and (self.estado != "borrador" or (old and old.estado != "borrador")):
                raise ValidationError("Un documento confirmado se modifica solo mediante sus servicios.")
            return super().save(*args, **kwargs)

    def validate_archive(self):
        raise ValidationError("Los documentos se cancelan o compensan, no se archivan.")

    def __str__(self):
        return str(self.codigo)


class LineaDocumento(BaseModel):
    documento_attr = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        parent = getattr(self, self.documento_attr)
        with transaction.atomic():
            parent = type(parent).objects.select_for_update().get(pk=parent.pk)
            if parent.estado != "borrador":
                raise ValidationError("No se pueden modificar líneas de un documento confirmado.")
            if self.pk:
                old = type(self).objects.get(pk=self.pk)
                if getattr(old, self.documento_attr + "_id") != parent.pk:
                    raise ValidationError("No se puede trasladar una línea a otro documento.")
            return super().save(*args, **kwargs)

    def validate_archive(self):
        if getattr(self, self.documento_attr).estado != "borrador":
            raise ValidationError("La línea pertenece a un documento confirmado.")


class LineaComercial(LineaDocumento):
    articulo = models.ForeignKey("apps_core.Articulo", on_delete=models.PROTECT, related_name="+")
    sku = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=16, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2)
    costo_personalizacion = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    descuento = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    tasa_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    especificaciones = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(condition=models.Q(cantidad__gt=0, precio_unitario__gte=0, costo_personalizacion__gte=0, descuento__gte=0, tasa_impuesto__gte=0, tasa_impuesto__lte=100), name="%(app_label)s_%(class)s_importes"),
            models.CheckConstraint(condition=models.Q(descuento__lte=models.F("cantidad")*models.F("precio_unitario") + models.F("costo_personalizacion")), name="%(app_label)s_%(class)s_descuento"),
        ]

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario + self.costo_personalizacion - self.descuento

    @property
    def total(self):
        return (self.subtotal * (Decimal("1") + self.tasa_impuesto / 100)).quantize(Decimal("0.01"))

    def clean(self):
        super().clean()
        if self.articulo_id and self.cantidad is not None:
            from apps.inventario.movimientos.services import validar_cantidad
            validar_cantidad(self.cantidad, self.articulo)

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class Cotizacion(BaseModel):
    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        EN_REVISION = "en_revision", "En revisión"
        APROBADA = "aprobada", "Aprobada internamente"
        ENVIADA = "enviada", "Enviada al cliente"
        ACEPTADA = "aceptada", "Aceptada por el cliente"
        RECHAZADA = "rechazada", "Rechazada"
        CANCELADA = "cancelada", "Cancelada"

    codigo = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cotizaciones",
    )

    # Datos del destinatario conservados para este documento.
    nombre_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    identificacion_cliente = models.CharField(
        max_length=30,
        blank=True,
    )
    direccion_cliente = models.TextField(blank=True)

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    moneda = models.CharField(
        max_length=3,
        choices=[("CLP", "Peso chileno")],
        default="CLP",
    )
    fecha_vencimiento = models.DateField()

    observaciones = models.TextField(blank=True)
    condiciones = models.TextField(blank=True)

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "cotización"
        verbose_name_plural = "cotizaciones"

    def __str__(self):
        return f"{self.codigo} - {self.nombre_cliente}"

    @property
    def esta_vencida(self):
        return self.fecha_vencimiento < timezone.localdate()

    @property
    def subtotal(self):
        return sum(
            (detalle.subtotal for detalle in self.detalles.all()),
            Decimal("0"),
        )

    @property
    def impuestos(self):
        return sum(
            (detalle.impuesto for detalle in self.detalles.all()),
            Decimal("0"),
        )

    @property
    def total(self):
        return sum(
            (detalle.total for detalle in self.detalles.all()),
            Decimal("0"),
        )


class DetalleCotizacion(BaseModel):
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.PROTECT,
        related_name="detalles",
    )
    variante = models.ForeignKey(
        "productos.VarianteProducto",
        on_delete=models.PROTECT,
        related_name="detalles_cotizacion",
    )
    orden = models.PositiveIntegerField(default=0)

    # Copias históricas tomadas al preparar la cotización.
    sku = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    especificaciones = models.JSONField(
        default=dict,
        blank=True,
    )

    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    # Importes netos para la línea completa, no por unidad.
    costo_personalizacion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    # Se asigna expresamente al cotizar.
    tasa_impuesto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
    )

    class Meta:
        ordering = ["orden", "pk"]
        verbose_name = "detalle de cotización"
        verbose_name_plural = "detalles de cotización"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="detalle_cot_cantidad_positiva",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(precio_unitario__gte=0)
                    & models.Q(costo_personalizacion__gte=0)
                    & models.Q(descuento__gte=0)
                ),
                name="detalle_cot_importes_validos",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(tasa_impuesto__gte=0)
                    & models.Q(tasa_impuesto__lte=100)
                ),
                name="detalle_cot_impuesto_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    descuento__lte=(
                        models.F("cantidad")
                        * models.F("precio_unitario")
                        + models.F("costo_personalizacion")
                    ),
                ),
                name="detalle_cot_descuento_valido",
            ),
        ]

    def __str__(self):
        return f"{self.sku} × {self.cantidad}"

    @property
    def importe_bruto(self):
        return (
            self.cantidad * self.precio_unitario
            + self.costo_personalizacion
        )

    @property
    def subtotal(self):
        return self.importe_bruto - self.descuento

    @property
    def impuesto(self):
        return self.subtotal * self.tasa_impuesto / Decimal("100")

    @property
    def total(self):
        return self.subtotal + self.impuesto

    def clean(self):
        super().clean()

        if (
            self.cantidad is not None
            and self.precio_unitario is not None
            and self.costo_personalizacion is not None
            and self.descuento is not None
            and self.descuento > self.importe_bruto
        ):
            raise ValidationError({
                "descuento": (
                    "El descuento no puede superar "
                    "el importe de la línea."
                ),
            })
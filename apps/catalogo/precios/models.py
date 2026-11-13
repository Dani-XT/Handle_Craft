from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class ListaPrecio(BaseModel):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    moneda = models.CharField(max_length=3, choices=[("CLP", "Peso chileno")], default="CLP")
    publica = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["moneda"], condition=models.Q(publica=True, activa=True, archived_at__isnull=True), name="precio_una_lista_publica")]


class PrecioArticulo(BaseModel):
    lista = models.ForeignKey(ListaPrecio, on_delete=models.PROTECT, related_name="precios")
    articulo = models.ForeignKey("apps_core.Articulo", on_delete=models.PROTECT, related_name="precios")
    cantidad_desde = models.DecimalField(max_digits=16, decimal_places=3, default=Decimal("1"))
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2)
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(cantidad_desde__gt=0, precio_unitario__gt=0), name="precio_tramo_importes_positivos"), models.CheckConstraint(condition=models.Q(vigente_hasta__isnull=True) | models.Q(vigente_hasta__gte=models.F("vigente_desde")), name="precio_tramo_fechas_validas")]

    def clean(self):
        super().clean()
        if not self.lista_id or not self.articulo_id or not self.vigente_desde:
            return
        from apps.inventario.movimientos.services import validar_cantidad
        validar_cantidad(self.cantidad_desde, self.articulo)
        qs = type(self).objects.filter(lista_id=self.lista_id, articulo_id=self.articulo_id, cantidad_desde=self.cantidad_desde, archived_at__isnull=True).exclude(pk=self.pk)
        qs = qs.filter(models.Q(vigente_hasta__isnull=True) | models.Q(vigente_hasta__gte=self.vigente_desde))
        if self.vigente_hasta:
            qs = qs.filter(vigente_desde__lte=self.vigente_hasta)
        if not self.is_archived and qs.exists():
            raise ValidationError("Ya existe un precio para ese tramo y período.")

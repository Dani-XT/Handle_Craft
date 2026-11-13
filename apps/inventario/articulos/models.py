from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class Articulo(BaseModel):
    class Seguimiento(models.TextChoices):
        CANTIDAD = "cantidad", "Por cantidad"
        LOTE = "lote", "Por lote"
        SERIE = "serie", "Por número de serie"

    categoria = models.ForeignKey("inventario_categorias.Categoria", on_delete=models.PROTECT, related_name="articulos")
    seguimiento = models.CharField(max_length=10, choices=Seguimiento.choices, default=Seguimiento.CANTIDAD)

    UNIDAD_CONTEO = "un"

    sku = models.CharField(max_length=50, unique=True,)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    unidad_medida = models.ForeignKey("unidades.UnidadMedida", on_delete=models.PROTECT, db_column="unidad_medida", default="un", related_name="articulos")

    es_vendible = models.BooleanField(default=False)
    es_comprable = models.BooleanField(default=True)
    es_consumible_en_produccion = models.BooleanField(default=False)

    class Meta:
        ordering = ["nombre", "pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(seguimiento__in=["cantidad", "lote", "serie"]), name="articulo_seguimiento_valido"),
            models.CheckConstraint(condition=~models.Q(seguimiento="serie") | models.Q(unidad_medida="un"), name="articulo_serie_unidad"),
        ]
        verbose_name = "artículo"
        verbose_name_plural = "artículos"

    def __str__(self):
        return f"{self.sku} - {self.nombre}"
    def clean(self):
        super().clean()
        if self.seguimiento == self.Seguimiento.SERIE and self.unidad_medida_id != self.UNIDAD_CONTEO:
            raise ValidationError({"unidad_medida": "Los artículos serializados se controlan en unidades."})
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values("seguimiento", "unidad_medida").first()
            if previous and (previous["seguimiento"] != self.seguimiento or previous["unidad_medida"] != self.unidad_medida_id):
                if self.existencias.exists() or self.lotes.exists() or self.series.exists():
                    raise ValidationError("No se puede cambiar unidad o seguimiento después de crear trazabilidad o existencias.")

    @property
    def requiere_serial(self):
        return self.seguimiento == self.Seguimiento.SERIE

    @property
    def stock_disponible(self):
        from apps.inventario.movimientos.selectors import stock_disponible
        return stock_disponible(self.pk)

    def validate_archive(self):
        if self.existencias.filter(cantidad__gt=0).exists():
            raise ValidationError("No se puede archivar un artículo con stock físico.")


class PresentacionArticulo(BaseModel):
    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name="presentaciones")
    nombre = models.CharField(max_length=80)
    unidad = models.ForeignKey("unidades.UnidadMedida", on_delete=models.PROTECT)
    cantidad_base = models.DecimalField(max_digits=16, decimal_places=3)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["articulo", "nombre"], name="presentacion_nombre_articulo_unico"), models.CheckConstraint(condition=models.Q(cantidad_base__gt=0), name="presentacion_factor_positivo")]

    def clean(self):
        super().clean()
        if self.articulo_id and self.cantidad_base is not None:
            from apps.inventario.movimientos.services import validar_cantidad
            validar_cantidad(self.cantidad_base, self.articulo)

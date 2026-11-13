from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class ArchiveQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(archived_at__isnull=True)

    def delete(self):
        raise ValidationError("El borrado masivo está deshabilitado. Archive cada registro indicando el responsable.")


class BaseModel(models.Model):
    objects = ArchiveQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def archive(self, actor=None):
        if self.is_archived:
            return
        self.validate_archive()
        self.archived_at = timezone.now()
        self.archived_by = actor
        self.updated_by = actor
        self.save(update_fields=["archived_at", "archived_by", "updated_by", "updated_at"])

    def validate_archive(self):
        pass

    def delete(self, using=None, keep_parents=False):
        self.archive()
        return (1, {self._meta.label: 1})

    created_at = models.DateTimeField("fecha de creación", auto_now_add=True,)
    updated_at = models.DateTimeField("fecha de actualización", auto_now=True,)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creado por",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="actualizado por",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )
    archived_at = models.DateTimeField(
        "fecha de archivado",
        null=True,
        blank=True,
        editable=False,
    )
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="archivado por",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        abstract = True

    @property
    def is_archived(self):
        return self.archived_at is not None


class Articulo(BaseModel):
    class Seguimiento(models.TextChoices):
        CANTIDAD = "cantidad", "Por cantidad"
        LOTE = "lote", "Por lote"
        SERIE = "serie", "Por número de serie"

    categoria = models.ForeignKey("inventario_categorias.Categoria", on_delete=models.PROTECT, related_name="articulos")
    seguimiento = models.CharField(max_length=10, choices=Seguimiento.choices, default=Seguimiento.CANTIDAD)

    class UnidadMedida(models.TextChoices):
        UNIDAD = "un", "Unidad"
        KILOGRAMO = "kg", "Kilogramo"
        METRO = "m", "Metro"
        LITRO = "l", "Litro"

    sku = models.CharField(max_length=50, unique=True,)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    unidad_medida = models.CharField(max_length=2, choices=UnidadMedida.choices, default=UnidadMedida.UNIDAD)

    es_vendible = models.BooleanField(default=False)
    es_comprable = models.BooleanField(default=True)
    es_consumible_en_produccion = models.BooleanField(default=False)

    class Meta:
        ordering = ["nombre", "pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(seguimiento__in=["cantidad", "lote", "serie"]), name="articulo_seguimiento_valido"),
            models.CheckConstraint(condition=~models.Q(seguimiento="serie") | models.Q(unidad_medida="un"), name="articulo_serie_unidad"),
            models.CheckConstraint(condition=models.Q(unidad_medida__in=["un", "kg", "m", "l"]), name="articulo_unidad_valida"),
        ]
        verbose_name = "artículo"
        verbose_name_plural = "artículos"

    def __str__(self):
        return f"{self.sku} - {self.nombre}"
    def clean(self):
        super().clean()
        if self.seguimiento == self.Seguimiento.SERIE and self.unidad_medida != self.UnidadMedida.UNIDAD:
            raise ValidationError({"unidad_medida": "Los artículos serializados se controlan en unidades."})
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values("seguimiento", "unidad_medida").first()
            if previous and (previous["seguimiento"] != self.seguimiento or previous["unidad_medida"] != self.unidad_medida):
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

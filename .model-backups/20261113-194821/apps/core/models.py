from django.conf import settings
from django.db import models


class BaseModel(models.Model):
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
        verbose_name = "artículo"
        verbose_name_plural = "artículos"

    def __str__(self):
        return f"{self.sku} - {self.nombre}"
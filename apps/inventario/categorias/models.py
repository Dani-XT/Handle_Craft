from django.db import models

from apps.core.models import BaseModel
from apps.core.utils import RenameImagen, image_exist


class Categoria(BaseModel):
    class Tipo(models.TextChoices):
        CONSUMIBLE = "consumible", "Consumible"
        EQUIPO = "equipo", "Equipo"

    nombre = models.CharField(
        max_length=100,
        unique=True,
    )
    descripcion = models.TextField(
        blank=True,
    )
    imagen = models.ImageField(
        upload_to=RenameImagen("categorias_inventario"),
        blank=True,
    )
    tipo = models.CharField(
        max_length=15,
        choices=Tipo.choices,
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoría de inventario"
        verbose_name_plural = "categorías de inventario"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    tipo__in=["consumible", "equipo"],
                ),
                name="categoria_inventario_tipo_valido",
            ),
        ]

    def __str__(self):
        return self.nombre

    @property
    def requiere_serial(self):
        return self.tipo == self.Tipo.EQUIPO

    @property
    def img(self):
        if image_exist(self.imagen):
            return self.imagen.url
        return None
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import ArchiveQuerySet, BaseModel
from apps.core.utils import RenameImagen, image_exist


class CategoriaQuerySet(ArchiveQuerySet):
    def internas(self):
        return self.filter(archived_at__isnull=True)

    def publicas(self):
        return self.internas().filter(publicada=True)


class Categoria(BaseModel):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to=RenameImagen("categorias"), blank=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True,
                               blank=True, related_name="subcategorias")
    publicada = models.BooleanField(default=False, db_index=True)
    orden = models.PositiveIntegerField(default=0)
    objects = CategoriaQuerySet.as_manager()

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        constraints = [models.CheckConstraint(
            condition=~models.Q(pk=models.F("parent_id")), name="categoria_no_autopadre")]

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()
        seen = {self.pk} if self.pk else set()
        parent = self.parent if self.parent_id else None
        while parent:
            if parent.pk in seen:
                raise ValidationError({"parent": "La jerarquía no puede formar un ciclo."})
            seen.add(parent.pk)
            parent = parent.parent

    def validate_archive(self):
        if self.subcategorias.filter(archived_at__isnull=True).exists() or self.articulos.filter(archived_at__isnull=True).exists() or self.productos.filter(archived_at__isnull=True).exists():
            raise ValidationError("La categoría aún tiene registros activos asociados.")

    @property
    def img(self):
        return self.imagen.url if image_exist(self.imagen) else None

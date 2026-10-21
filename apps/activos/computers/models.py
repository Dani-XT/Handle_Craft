from django.db import models

from apps.activos.categories.models import Categoria

# Create your models here.
class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, help_text="Código interno o SKU.",)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos",)
    nombre = models.CharField(max_length=200,)
    descripcion = models.TextField(blank=True,)
    activo = models.BooleanField(default=True,)

    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        ordering = ("nombre",)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

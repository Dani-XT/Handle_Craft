from django.db import models

from apps.core.utils import RenameImagen

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField()
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to=RenameImagen("categorias_catalogo/"))


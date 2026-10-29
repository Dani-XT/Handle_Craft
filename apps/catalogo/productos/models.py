from django.db import models
from apps.core.utils import RenameImagen

from apps.catalogo.categorias.models import Categoria

# Create your models here.
class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")

    nombre = models.CharField()
    descripcion = models.TextField()
    tamaño = models.CharField()

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to=RenameImagen("productos"))


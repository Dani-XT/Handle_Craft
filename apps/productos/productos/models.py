from django.db import models
from apps.core.utils import RenameImagen

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField()
    descripcion = models.TextField()
    tamaño = models.CharField()

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to=RenameImagen("productos"))


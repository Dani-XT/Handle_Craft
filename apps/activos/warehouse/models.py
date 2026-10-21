from django.db import models

# Create your models here.
class Bodega(models.Model):
    nombre = models.CharField(max_length=254)
    descripcion = models.TextField()

    direccion = models.TextField()
    
    imagen = models.ImageField(upload_to='bodega/', blank=True, null=True)
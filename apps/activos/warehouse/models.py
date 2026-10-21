from django.db import models

# Create your models here.
class Bodega(models.Model):
    nombre = models.CharField(max_length=254)
    direccion = models.TextField()
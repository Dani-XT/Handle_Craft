from django.db import models

# Create your models here.
class Sugerencia(models.Model):
    nombre_completo = models.CharField(max_length=254)
    email = models.EmailField()
    mensaje = models.TextField()


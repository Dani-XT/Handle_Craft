from django.db import models
from apps.core.utils import image_exist


# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to="categorias/")

    @property
    def img(self):
        if image_exist(self.avatar):
            return self.avatar.url
        else:
            return None
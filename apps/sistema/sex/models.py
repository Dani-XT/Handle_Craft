from django.db import models
from automation_ticket.utils.image.utils import image_exist

# Create your models here.
class Sexo(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=200)
    avatar = models.ImageField(upload_to="sexos/", default='sexos/otro.png')
    
    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ("nombre",)
        verbose_name = "sexo"
        verbose_name_plural = "sexos"

    def __str__(self):
        return self.nombre
    
    @property
    def img(self):
        if image_exist(self.avatar):
            return self.avatar.url
        else:
            return None
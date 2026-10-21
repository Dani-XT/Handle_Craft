from django.db import models
from automation_ticket.utils.image.utils import image_exist

# Create your models here.
class Sede(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=200, default='')
    imagen = models.ImageField(upload_to="sedes/", blank=True, null=True)

    def __str__(self):
        return self.nombre
    
    @property
    def img(self):
        if image_exist(self.imagen):
            return self.imagen.url
        else:
            return None

class Edificio(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre
    
class Campus(models.Model):
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name="campus")
    nombre = models.CharField(max_length=150)
    imagen_light = models.ImageField(upload_to='campus/', blank=True, null=True)
    imagen_dark = models.ImageField(upload_to='campus/', blank=True, null=True)
    
    descripcion = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.nombre
    
    @property
    def img(self):
        if image_exist(self.imagen_light) or image_exist(self.imagen_dark):
            return True
        return None
    
    # @property
    # def img_light(self):
    #     if self.imagen_light and self.imagen_light.name:
    #         return self.imagen_light.url
    #     return None
    
    # @property
    # def img_dark(self):
    #     if self.imagen_dark and self.imagen_dark.name:
    #         return self.imagen_dark.url
    #     return None
    
    @property
    def get_sede(self):
        return self.sede.nombre
    
# class UbicacionManager(models.Manager):
#     def por_sede(self, sede):
#         return self.filter(sede=sede)
    
#     def por_edificio(self, edificio):
#         return self.filter(edificio=edificio)
    
#     def por_sede_edificio(self, sede, edificio):
#         return self.filter(sede=sede, edificio=edificio)

class Direccion(models.Model):
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name="ubicaciones", blank=True, null=True)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="ubicaciones")
    
    direccion = models.CharField(max_length=150)
    
    # objects = UbicacionManager()

    @property
    def get_campus(self):
        return self.campus.nombre if self.campus else ""
    
    def get_edificio(self):
        return self.edificio.nombre if self.edificio else ""
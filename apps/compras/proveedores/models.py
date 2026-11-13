from django.db import models
from apps.core.models import BaseModel


class Proveedor(BaseModel):
    nombre = models.CharField(max_length=200)
    identificacion = models.CharField(max_length=30, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class ContactoProveedor(BaseModel):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="contactos")
    nombre = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)


class ArticuloProveedor(BaseModel):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="articulos")
    articulo = models.ForeignKey("apps_core.Articulo", on_delete=models.PROTECT, related_name="proveedores")
    codigo_proveedor = models.CharField(max_length=80)
    plazo_dias = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["proveedor", "articulo"], name="proveedor_articulo_unico"), models.UniqueConstraint(fields=["proveedor", "codigo_proveedor"], name="proveedor_codigo_unico")]

from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class Cliente(BaseModel):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="cliente")
    nombre = models.CharField(max_length=200)
    identificacion = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)

    def clean(self):
        super().clean()
        self.identificacion = self.identificacion.strip() or None if self.identificacion else None

    def __str__(self):
        return self.nombre


class DireccionCliente(BaseModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="direcciones")
    nombre = models.CharField(max_length=80)
    direccion = models.TextField()
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    principal = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["cliente"], condition=models.Q(principal=True, archived_at__isnull=True), name="cliente_una_direccion_principal")]


class ContactoCliente(BaseModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="contactos")
    nombre = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    cargo = models.CharField(max_length=100, blank=True)

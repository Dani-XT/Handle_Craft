from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = None

    email = models.EmailField(
        verbose_name="correo electrónico",
        unique=True,
    )

    rut = models.CharField(
        verbose_name="RUT",
        max_length=12,
        unique=True,
        null=True,
        blank=True,
    )

    sexo = models.ForeignKey(
        "sex.Sexo",
        on_delete=models.SET_NULL,
        related_name="tecnicos",
        null=True,
        blank=True,
    )

    direccion = models.ForeignKey(
        "locations.Direccion",
        on_delete=models.SET_NULL,
        related_name="tecnicos",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ("first_name", "last_name")
        verbose_name = "tecnico"
        verbose_name_plural = "tecnicos"

    def __str__(self):
        return self.email

    @property
    def img(self):
        if not self.sexo:
            return None

        return self.sexo.img

    @property
    def get_direccion(self):
        if self.direccion:
            return self.direccion.direccion

        return "N/A"

    @property
    def get_full_direccion(self):
        if not self.direccion:
            return "N/A"

        if self.direccion.edificio:
            return (
                f"{self.direccion.edificio.nombre} - "
                f"{self.direccion.direccion}"
            )

        return self.direccion.direccion

    @property
    def get_edificio(self):
        if self.direccion and self.direccion.edificio:
            return self.direccion.edificio.nombre

        return "N/A"

    @property
    def get_campus(self):
        if self.direccion:
            return self.direccion.campus.nombre

        return "N/A"

    

    @property
    def get_sede(self):
        if self.direccion:
            return self.direccion.campus.sede.nombre

        return "N/A"

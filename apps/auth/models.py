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
        "sexo.Sexo",
        on_delete=models.SET_NULL,
        related_name="tecnicos",
        null=True,
        blank=True,
    )


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

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
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = models.CharField(
        verbose_name="nombre de usuario",
        max_length=150,
        unique=True,
        editable=False,
    )

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

    email_token = models.CharField(max_length=100, blank=True, null=True)
    forget_password_token = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)





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

    @staticmethod
    def username_from_email(email):
        normalized_email = (email or "").strip().lower()
        validate_email(normalized_email)

        username = normalized_email.rsplit("@", 1)[0]

        if len(username) > 150:
            raise ValidationError(
                "La parte del correo anterior al dominio "
                "no puede superar los 150 caracteres."
            )

        return username

    
    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")

        # Normalizar nombres y apellidos
        if update_fields is None or "first_name" in update_fields:
            self.first_name = " ".join(
                self.first_name.split()
            ).title()

        if update_fields is None or "last_name" in update_fields:
            self.last_name = " ".join(
                self.last_name.split()
            ).title()

        # Sincronizar username con email
        sync_username = (
            update_fields is None
            or "email" in update_fields
            or "username" in update_fields
        )

        if sync_username:
            self.email = (self.email or "").strip().lower()
            self.username = self.username_from_email(self.email)

            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {
                    "email",
                    "username",
                }

        return super().save(*args, **kwargs)

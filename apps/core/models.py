from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True,)
    updated_at = models.DateTimeField("fecha de actualización", auto_now=True,)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creado por",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="actualizado por",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )

    archived_at = models.DateTimeField(
        "fecha de archivado",
        null=True,
        blank=True,
        editable=False,
    )

    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="archivado por",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        abstract = True

    @property
    def is_archived(self):
        return self.archived_at is not None
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class ArchiveQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(archived_at__isnull=True)

    def delete(self):
        raise ValidationError("El borrado masivo está deshabilitado. Archive cada registro indicando el responsable.")


class BaseModel(models.Model):
    objects = ArchiveQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def archive(self, actor=None):
        if self.is_archived:
            return
        self.validate_archive()
        self.archived_at = timezone.now()
        self.archived_by = actor
        self.updated_by = actor
        self.save(update_fields=["archived_at", "archived_by", "updated_by", "updated_at"])

    def validate_archive(self):
        pass

    def delete(self, using=None, keep_parents=False):
        self.archive()
        return (1, {self._meta.label: 1})

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



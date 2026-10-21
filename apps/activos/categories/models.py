from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
import os
import uuid

from apps.core.utils import image_exist



# ------------------------------------------------------------------------
# CATEGORIA Y COLUMNAS
# ------------------------------------------------------------------------
class TipoControlInventario(models.TextChoices):
    SERIALIZADO = "serializado", "Activo serializado"
    STOCK = "stock", "Insumo controlado por stock"

class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True,)
    tipo_control = models.CharField(max_length=20, choices=TipoControlInventario.choices,)
    descripcion = models.TextField(blank=True,)
    activa = models.BooleanField(default=True,)

    imagen = models.ImageField(upload_to="categorias/", blank=True,)

    atributos = models.ManyToManyField("AtributoDefinido", through="CategoriaAtributo", related_name="categorias",)

    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        ordering = ("nombre",)
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre

    @property
    def es_serializada(self):
        return (self.tipo_control == TipoControlInventario.SERIALIZADO)

    @property
    def es_stock(self):
        return (self.tipo_control == TipoControlInventario.STOCK)

    @property
    def img(self):
        if self.imagen and image_exist(self.imagen):
            return self.imagen.url

        return None

class TipoDatoAtributo(models.TextChoices):
    TEXTO = "texto", "Texto"
    ENTERO = "entero", "Número entero"
    DECIMAL = "decimal", "Número decimal"
    FECHA = "fecha", "Fecha"
    BOOLEANO = "booleano", "Sí/No"
    OPCION = "opcion", "Lista de opciones"

class AtributoDefinido(models.Model):
    codigo = models.SlugField(max_length=80, unique=True, help_text="Identificador interno, por ejemplo: memoria_ram",)
    nombre = models.CharField(max_length=100,)
    tipo_dato = models.CharField(max_length=20, choices=TipoDatoAtributo.choices, default=TipoDatoAtributo.TEXTO,)
    unidad = models.CharField(max_length=30, blank=True, help_text="Ejemplo: GB, TB, pulgadas, MHz.")
    descripcion = models.TextField(blank=True,)
    activo = models.BooleanField(default=True,)

    class Meta:
        ordering = ("nombre",)
        verbose_name = "atributo definido"
        verbose_name_plural = "atributos definidos"

    def __str__(self):
        if self.unidad:
            return f"{self.nombre} ({self.unidad})"

        return self.nombre

class CategoriaAtributo(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="configuracion_atributos")
    atributo = models.ForeignKey(AtributoDefinido, on_delete=models.PROTECT, related_name="configuraciones_categoria",)

    obligatorio = models.BooleanField(default=False,)

    orden = models.PositiveSmallIntegerField(default=0,)

    texto_ayuda = models.CharField(max_length=255, blank=True,)

    valor_predeterminado = models.JSONField(blank=True, null=True,)

    class Meta:
        ordering = ("orden", "atributo__nombre")
        constraints = [
            models.UniqueConstraint(
                fields=("categoria", "atributo"),
                name="unique_atributo_por_categoria",
            )
        ]

    def __str__(self):
        return (
            f"{self.categoria} - "
            f"{self.atributo}"
        )

class AtributoOpcion(models.Model):
    atributo = models.ForeignKey(AtributoDefinido, on_delete=models.CASCADE, related_name="opciones",)
    valor = models.CharField(max_length=100,)
    etiqueta = models.CharField(max_length=100,)
    orden = models.PositiveSmallIntegerField(default=0,)
    activa = models.BooleanField(default=True,)
    class Meta:
        ordering = ("orden", "etiqueta")
        constraints = [
            models.UniqueConstraint(
                fields=("atributo", "valor"),
                name="unique_opcion_por_atributo",
            )
        ]

    def __str__(self):
        return self.etiqueta

from django.core.exceptions import ValidationError


class AtributoValor(models.Model):
    # producto = models.ForeignKey(
    #     Producto,
    #     on_delete=models.CASCADE,
    #     related_name="valores_atributos",
    # )

    configuracion = models.ForeignKey(
        CategoriaAtributo,
        on_delete=models.PROTECT,
        related_name="valores",
    )

    valor = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("producto", "configuracion"),
                name="unique_valor_atributo_por_producto",
            )
        ]

    def clean(self):
        super().clean()

        if (
            self.producto_id
            and self.configuracion_id
            and self.producto.categoria_id
            != self.configuracion.categoria_id
        ):
            raise ValidationError(
                {
                    "configuracion": (
                        "Este atributo no pertenece a la "
                        "categoría del producto."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.producto} - "
            f"{self.configuracion.atributo.nombre}: "
            f"{self.valor}"
        )
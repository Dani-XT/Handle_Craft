from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import Articulo, BaseModel
from apps.core.utils import RenameImagen, image_exist

class TipoProducto(BaseModel):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "tipo de producto"
        verbose_name_plural = "tipos de producto"

    def __str__(self):
        return self.nombre


class Producto(BaseModel):
    categoria = models.ForeignKey(
        "catalogo_categorias.Categoria",
        on_delete=models.PROTECT,
        related_name="productos",
    )
    tipo_producto = models.ForeignKey(
        TipoProducto,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
    )

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    permite_personalizacion = models.BooleanField(default=False)
    publicado = models.BooleanField(default=False)

    class Meta:
        ordering = ["nombre", "pk"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre


class VarianteProducto(BaseModel):
    class TipoAsa(models.TextChoices):
        SIN_ASA = "sin_asa", "Sin asa"
        PLANA = "plana", "Plana"
        TORCIDA = "torcida", "Torcida"
        TROQUELADA = "troquelada", "Troquelada"

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="variantes",
    )
    articulo = models.OneToOneField(
        Articulo,
        on_delete=models.PROTECT,
        related_name="variante_catalogo",
    )

    color = models.CharField(max_length=50)
    tipo_asa = models.CharField(
        max_length=20,
        choices=TipoAsa.choices,
        default=TipoAsa.SIN_ASA,
    )

    # Esta primera versión representa bolsas con fuelle.
    # Las medidas son interiores útiles, en milímetros.
    ancho_mm = models.PositiveIntegerField(validators=[MinValueValidator(1)],)
    alto_mm = models.PositiveIntegerField(validators=[MinValueValidator(1)],)
    fuelle_mm = models.PositiveIntegerField(validators=[MinValueValidator(1)],)
    gramaje_g_m2 = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    # Vacío significa que no se ha verificado la carga.
    carga_maxima_kg = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, validators=[MinValueValidator(Decimal("0.001"))])

    # Precio neto por bolsa, sin personalización.
    precio_base = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))],)
    moneda = models.CharField(max_length=3, choices=[("CLP", "Peso chileno")], default="CLP")

    cantidad_minima = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)],)
    multiplo_venta = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    disponible_para_venta = models.BooleanField(default=True)

    class Meta:
        ordering = ["producto_id", "articulo__sku"]
        verbose_name = "variante de producto"
        verbose_name_plural = "variantes de producto"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(ancho_mm__gt=0)
                    & models.Q(alto_mm__gt=0)
                    & models.Q(fuelle_mm__gt=0)
                    & models.Q(gramaje_g_m2__gt=0)
                ),
                name="variante_medidas_positivas",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(carga_maxima_kg__isnull=True)
                    | models.Q(carga_maxima_kg__gt=0)
                ),
                name="variante_carga_valida",
            ),
            models.CheckConstraint(
                condition=models.Q(precio_base__gt=0),
                name="variante_precio_positivo",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(cantidad_minima__gt=0)
                    & models.Q(multiplo_venta__gt=0)
                ),
                name="variante_cantidades_positivas",
            ),
        ]

    def __str__(self):
        return f"{self.articulo.sku} - {self.producto.nombre}"

    @property
    def sku(self):
        return self.articulo.sku

    def clean(self):
        super().clean()

        if not self.articulo_id:
            return

        errores = []

        if not self.articulo.es_vendible:
            errores.append("El artículo debe ser vendible.")

        if ( self.articulo.unidad_medida != Articulo.UnidadMedida.UNIDAD):
            errores.append("Las variantes de bolsas se venden en unidades.")

        if errores:
            raise ValidationError({"articulo": errores})


class ImagenProducto(BaseModel):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="imagenes")
    variante = models.ForeignKey(VarianteProducto, on_delete=models.PROTECT, related_name="imagenes", null=True, blank=True)

    imagen = models.ImageField(upload_to=RenameImagen("productos"))
    texto_alternativo = models.CharField(max_length=200, blank=True,)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "pk"]
        verbose_name = "imagen de producto"
        verbose_name_plural = "imágenes de producto"

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

    def clean(self):
        super().clean()

        if (
            self.variante_id
            and self.producto_id
            and self.variante.producto_id != self.producto_id
        ):
            raise ValidationError({
                "variante": (
                    "La variante debe pertenecer al producto "
                    "seleccionado."
                ),
            })

    @property
    def img(self):
        if image_exist(self.imagen):
            return self.imagen.url
        return None
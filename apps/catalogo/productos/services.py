from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Producto
from apps.catalogo.precios.selectors import precio_para


@transaction.atomic
def publicar_producto(producto_id, actor=None):
    producto = Producto.objects.select_for_update().get(pk=producto_id, archived_at__isnull=True)
    variantes = list(producto.variantes.filter(archived_at__isnull=True, disponible_para_venta=True))
    if not variantes:
        raise ValidationError("El producto necesita al menos una variante disponible.")
    for variante in variantes:
        variante.full_clean()
        if not precio_para(variante.articulo_id, variante.cantidad_minima):
            raise ValidationError("Cada variante necesita un precio público vigente para su cantidad mínima.")
    producto.publicado = True
    producto.updated_by = actor
    producto.full_clean()
    producto.save(update_fields=["publicado", "updated_by", "updated_at"])
    return producto

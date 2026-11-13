from django.db import transaction
from .models import ListaPrecio, PrecioArticulo


@transaction.atomic
def guardar_precio(precio, actor=None):
    ids = {precio.lista_id}
    if precio.pk:
        anterior = PrecioArticulo.objects.filter(pk=precio.pk).values_list("lista_id", flat=True).first()
        if anterior:
            ids.add(anterior)
    list(ListaPrecio.objects.select_for_update().filter(pk__in=ids).order_by("pk"))
    precio.updated_by = actor
    if not precio.pk:
        precio.created_by = actor
    precio.save()
    return precio

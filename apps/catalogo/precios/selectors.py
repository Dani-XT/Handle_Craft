from django.db.models import Q
from django.utils import timezone
from .models import PrecioArticulo


def precio_para(articulo_id, cantidad, lista_id=None, fecha=None):
    fecha = fecha or timezone.localdate()
    qs = PrecioArticulo.objects.filter(articulo_id=articulo_id, articulo__archived_at__isnull=True, archived_at__isnull=True, lista__activa=True, lista__archived_at__isnull=True, cantidad_desde__lte=cantidad, vigente_desde__lte=fecha).filter(Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=fecha))
    qs = qs.filter(lista_id=lista_id) if lista_id else qs.filter(lista__publica=True)
    return qs.order_by("-cantidad_desde").first()

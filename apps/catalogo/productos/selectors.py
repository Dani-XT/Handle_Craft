from .models import Producto


def productos_publicos():
    return Producto.objects.filter(
        publicado=True, archived_at__isnull=True,
        categoria__publicada=True, categoria__archived_at__isnull=True,
        variantes__archived_at__isnull=True, variantes__disponible_para_venta=True,
        variantes__articulo__es_vendible=True, variantes__articulo__archived_at__isnull=True,
    ).distinct()

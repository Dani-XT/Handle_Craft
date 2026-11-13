from decimal import Decimal
from django.db.models import F, Q, Sum
from django.utils import timezone
from .models import Existencia, ReservaInventario


def existencias_despachables():
    hoy = timezone.localdate()
    return Existencia.objects.filter(
        archived_at__isnull=True, articulo__archived_at__isnull=True,
        ubicacion__archived_at__isnull=True, ubicacion__bodega__archived_at__isnull=True,
        ubicacion__bodega__activa=True, ubicacion__condicion="disponible",
        ubicacion__permite_despacho=True, lote__archived_at__isnull=True,
        unidad_serializada__archived_at__isnull=True,
        unidad_serializada__lote__archived_at__isnull=True,
    ).filter(Q(lote__fecha_vencimiento__isnull=True) | Q(lote__fecha_vencimiento__gte=hoy)).filter(
        Q(unidad_serializada__lote__fecha_vencimiento__isnull=True) |
        Q(unidad_serializada__lote__fecha_vencimiento__gte=hoy)
    )


def stock_disponible(articulo_id, bodega_id=None):
    saldos = existencias_despachables().filter(articulo_id=articulo_id)
    if bodega_id is not None:
        saldos = saldos.filter(ubicacion__bodega_id=bodega_id)
    fisico = saldos.aggregate(total=Sum("cantidad"))["total"] or Decimal("0")
    reservado = ReservaInventario.objects.filter(existencia__in=saldos).aggregate(
        total=Sum(F("cantidad") - F("despachada") - F("liberada"))
    )["total"] or Decimal("0")
    return fisico - reservado

from decimal import Decimal
from django.conf import settings
from django.db import models
from apps.core.documents import DocumentoBase, LineaComercial


class Pedido(DocumentoBase):
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="pedidos")
    cotizacion = models.OneToOneField("cotizaciones.Cotizacion", on_delete=models.PROTECT, null=True, blank=True, related_name="pedido")
    moneda = models.CharField(max_length=3, choices=[("CLP", "Peso chileno")], default="CLP")
    nombre_cliente = models.CharField(max_length=200)
    direccion_entrega = models.TextField()

    @property
    def total(self):
        return sum((d.total for d in self.detalles.filter(archived_at__isnull=True)), Decimal("0"))


class DetallePedido(LineaComercial):
    documento_attr = "pedido"
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name="detalles")
    detalle_cotizacion = models.OneToOneField("cotizaciones.DetalleCotizacion", on_delete=models.PROTECT, null=True, blank=True)


class HistorialEstadoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name="historial")
    anterior = models.CharField(max_length=12)
    nuevo = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        default_permissions = ("view",)

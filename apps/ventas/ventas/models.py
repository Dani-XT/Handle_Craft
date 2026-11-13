from decimal import Decimal
from django.db import models
from apps.core.documents import DocumentoBase, LineaComercial


class Venta(DocumentoBase):
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="ventas")
    pedido = models.OneToOneField("pedidos.Pedido", on_delete=models.PROTECT, related_name="venta")
    moneda = models.CharField(max_length=3, choices=[("CLP", "Peso chileno")], default="CLP")
    nombre_cliente = models.CharField(max_length=200)

    @property
    def total(self):
        return sum((d.total for d in self.detalles.filter(archived_at__isnull=True)), Decimal("0"))


class DetalleVenta(LineaComercial):
    documento_attr = "venta"
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name="detalles")
    detalle_pedido = models.OneToOneField("pedidos.DetallePedido", on_delete=models.PROTECT)

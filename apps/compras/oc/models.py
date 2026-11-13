from decimal import Decimal
from django.db import models
from apps.core.documents import DocumentoBase, LineaComercial


class OrdenCompra(DocumentoBase):
    proveedor = models.ForeignKey("proveedores.Proveedor", on_delete=models.PROTECT, related_name="ordenes")
    moneda = models.CharField(max_length=3, choices=[("CLP", "Peso chileno")], default="CLP")
    direccion_entrega = models.TextField()

    @property
    def total(self):
        return sum((d.total for d in self.detalles.filter(archived_at__isnull=True)), Decimal("0"))


class DetalleOrdenCompra(LineaComercial):
    documento_attr = "orden"
    orden = models.ForeignKey(OrdenCompra, on_delete=models.PROTECT, related_name="detalles")

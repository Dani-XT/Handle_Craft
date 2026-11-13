from django.db import models
from django.core.exceptions import ValidationError
from apps.core.documents import DocumentoBase, LineaDocumento


class Despacho(DocumentoBase):
    pedido = models.ForeignKey("pedidos.Pedido", on_delete=models.PROTECT, related_name="despachos")
    direccion_entrega = models.TextField()
    transportista = models.CharField(max_length=100, blank=True)
    seguimiento = models.CharField(max_length=100, blank=True)
    operacion = models.OneToOneField("movimientos.OperacionInventario", on_delete=models.PROTECT, null=True, blank=True, editable=False)


class DetalleDespacho(LineaDocumento):
    documento_attr = "despacho"
    despacho = models.ForeignKey(Despacho, on_delete=models.PROTECT, related_name="detalles")
    detalle_pedido = models.ForeignKey("pedidos.DetallePedido", on_delete=models.PROTECT, related_name="despachos")
    reserva = models.ForeignKey("movimientos.ReservaInventario", on_delete=models.PROTECT, related_name="despachos")
    cantidad = models.DecimalField(max_digits=16, decimal_places=3)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(cantidad__gt=0), name="despacho_cantidad_positiva")]

    def clean(self):
        super().clean()
        if self.despacho_id and self.detalle_pedido_id and self.detalle_pedido.pedido_id != self.despacho.pedido_id:
            raise ValidationError("El detalle pertenece a otro pedido.")
        if self.reserva_id and self.detalle_pedido_id and self.reserva.detalle_pedido_id != self.detalle_pedido_id:
            raise ValidationError("La reserva debe pertenecer a la misma línea de pedido.")

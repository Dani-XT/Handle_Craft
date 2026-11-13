from django.db import models
from django.core.exceptions import ValidationError
from apps.core.documents import DocumentoBase, LineaDocumento


class RecepcionCompra(DocumentoBase):
    orden = models.ForeignKey("oc.OrdenCompra", on_delete=models.PROTECT, related_name="recepciones")
    documento_proveedor = models.CharField(max_length=100)
    operacion = models.OneToOneField("movimientos.OperacionInventario", on_delete=models.PROTECT, null=True, blank=True, editable=False)


class DetalleRecepcion(LineaDocumento):
    documento_attr = "recepcion"
    recepcion = models.ForeignKey(RecepcionCompra, on_delete=models.PROTECT, related_name="detalles")
    detalle_orden = models.ForeignKey("oc.DetalleOrdenCompra", on_delete=models.PROTECT, related_name="recepciones")
    destino = models.ForeignKey("movimientos.Existencia", on_delete=models.PROTECT, null=True, blank=True)
    cantidad_aceptada = models.DecimalField(max_digits=16, decimal_places=3, default=0)
    cantidad_rechazada = models.DecimalField(max_digits=16, decimal_places=3, default=0)
    motivo_rechazo = models.TextField(blank=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(cantidad_aceptada__gte=0, cantidad_rechazada__gte=0) & (models.Q(cantidad_aceptada__gt=0) | models.Q(cantidad_rechazada__gt=0)), name="recepcion_cantidades_validas")]

    def clean(self):
        super().clean()
        if self.recepcion_id and self.detalle_orden_id and self.detalle_orden.orden_id != self.recepcion.orden_id:
            raise ValidationError("La línea no pertenece a la orden de esta recepción.")
        if self.cantidad_aceptada and (not self.destino_id or self.destino.articulo_id != self.detalle_orden.articulo_id):
            raise ValidationError("El destino debe corresponder al artículo recibido.")
        if self.cantidad_rechazada and not self.motivo_rechazo.strip():
            raise ValidationError("Indique el motivo del rechazo.")

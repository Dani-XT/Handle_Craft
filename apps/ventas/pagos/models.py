import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel
from apps.core.documents import DocumentoBase


class Pago(DocumentoBase):
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="pagos")
    moneda = models.CharField(max_length=3, choices=[("CLP", "Peso chileno")], default="CLP")
    importe = models.DecimalField(max_digits=14, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=[("transferencia", "Transferencia"), ("efectivo", "Efectivo"), ("tarjeta", "Tarjeta")])
    referencia = models.CharField(max_length=100, blank=True)

    class Meta(DocumentoBase.Meta):
        abstract = False
        constraints = DocumentoBase.Meta.constraints + [models.CheckConstraint(condition=models.Q(importe__gt=0), name="pago_importe_positivo")]


class RegistroPago(BaseModel):
    clave = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    importe = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        abstract = True
        constraints = [models.CheckConstraint(condition=models.Q(importe__gt=0), name="%(app_label)s_%(class)s_positivo")]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Los registros financieros se compensan, no se editan.")
        return super().save(*args, **kwargs)

    def validate_archive(self):
        raise ValidationError("Los registros financieros no se archivan.")


class AplicacionPago(RegistroPago):
    pago = models.ForeignKey(Pago, on_delete=models.PROTECT, related_name="aplicaciones")
    pedido = models.ForeignKey("pedidos.Pedido", on_delete=models.PROTECT, related_name="aplicaciones_pago")

    def clean(self):
        super().clean()
        if self.pago_id and self.pedido_id and (self.pago.cliente_id != self.pedido.cliente_id or self.pago.moneda != self.pedido.moneda):
            raise ValidationError("El cliente y la moneda deben coincidir.")


class Reembolso(RegistroPago):
    aplicacion = models.ForeignKey(AplicacionPago, on_delete=models.PROTECT, related_name="reembolsos")
    motivo = models.TextField()

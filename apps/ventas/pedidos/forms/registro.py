from django import forms
from ..models import Pedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ('cliente', 'nombre_cliente', 'direccion_entrega', 'moneda', 'fecha', 'observaciones')

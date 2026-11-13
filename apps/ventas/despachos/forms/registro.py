from django import forms
from ..models import Despacho


class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ('pedido', 'direccion_entrega', 'transportista', 'seguimiento', 'fecha', 'observaciones')

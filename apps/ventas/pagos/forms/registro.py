from django import forms
from ..models import Pago


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ('cliente', 'moneda', 'importe', 'metodo', 'referencia', 'fecha', 'observaciones')

from django import forms
from ..models import RecepcionCompra


class RecepcionCompraForm(forms.ModelForm):
    class Meta:
        model = RecepcionCompra
        fields = ('orden', 'documento_proveedor', 'fecha', 'observaciones')

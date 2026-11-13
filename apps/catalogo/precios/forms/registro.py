from django import forms
from ..models import PrecioArticulo


class PrecioArticuloForm(forms.ModelForm):
    class Meta:
        model = PrecioArticulo
        fields = ('lista', 'articulo', 'cantidad_desde', 'precio_unitario', 'vigente_desde', 'vigente_hasta')

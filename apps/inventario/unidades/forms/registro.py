from django import forms
from ..models import UnidadMedida


class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ('codigo', 'nombre', 'simbolo', 'magnitud', 'decimales')

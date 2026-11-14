from django import forms

from apps.inventario.bodegas.models import Bodega

class BodegasAddForm(forms.ModelForm):
    nombre = forms.CharField()

    class Meta:
        model = Bodega
        fields = (
            "nombre",
        )

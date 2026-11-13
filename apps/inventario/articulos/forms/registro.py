from django import forms
from ..models import Articulo


class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ('sku', 'nombre', 'descripcion', 'categoria', 'unidad_medida', 'seguimiento', 'es_vendible', 'es_comprable', 'es_consumible_en_produccion')

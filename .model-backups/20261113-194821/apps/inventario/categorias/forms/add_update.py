from django import forms

from apps.inventario.categorias.models import Categoria

class CategoriaInventarioAddUpdateForm(forms.ModelForm):
    nombre = forms.CharField()
    descripcion = forms.Textarea()

    class Meta:
        model = Categoria
        fields = (
            "nombre",
        )
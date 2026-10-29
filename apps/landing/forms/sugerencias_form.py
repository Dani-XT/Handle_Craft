from django import forms

class SugerenciasForm(forms.Form):
    nombre_completo = forms.CharField(max_length=254)
    email = forms.EmailField()
    descripcion = forms.Textarea()

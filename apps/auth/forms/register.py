from django import forms
from django.db import transaction
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model

Usuario = get_user_model()


class RegisterUsuarioForm():
    nombre = forms.CharField(max_length=150)
    apellido = forms.CharField(max_length=150)
    rut = forms.CharField(max_length=12)
    telefono = forms.CharField(max_length=20)
    fecha_nacimiento = forms.CharField()
    # sexo = forms.ChoiceField(choices=Usuario.sexo.choices, required=True)
    email = forms.EmailField()
    password = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



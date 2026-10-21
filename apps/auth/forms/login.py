from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = None

    def clean(self):
        data = super().clean()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            raise ValidationError("Debes ingresar correo y contraseña")

        usuario = authenticate(username=email, password=password)

        if usuario is None:
            raise ValidationError("Correo o contraseña incorrectos.")

        if not usuario.is_active:
            raise ValidationError("La cuenta se encuentra desactivada.")

        self.usuario = usuario
        return data

    def save(self):
        return self.usuario
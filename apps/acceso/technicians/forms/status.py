from django import forms


class TechnicianStatusForm(forms.Form):
    ACTION_ACTIVATE = "activate"
    ACTION_DEACTIVATE = "deactivate"

    ACTION_CHOICES = (
        (ACTION_ACTIVATE, "Activar"),
        (ACTION_DEACTIVATE, "Desactivar"),
    )

    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.HiddenInput)
    confirm = forms.BooleanField(required=True, error_messages={"required": "Debes confirmar la operación."},)
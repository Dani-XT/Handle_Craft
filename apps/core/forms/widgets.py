from django import forms

class FloatingInput(forms.TextInput):
    template_name = "widgets/floating_input.html"


class TextAreaInput(forms.Textarea):
    template_name = "widgets/textarea_input.html"


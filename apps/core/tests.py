from django import forms
from django.test import SimpleTestCase

from apps.core.forms import StyledForm
from apps.core.forms.widgets import (
    CheckboxInput,
    FileInput,
    FloatingEmailInput,
    FloatingInput,
    QuillEditorWidget,
    SelectInput,
)


class ExampleStyledForm(StyledForm):
    rich_text_fields = ("contenido",)

    nombre = forms.CharField()
    email = forms.EmailField()
    categoria = forms.ChoiceField(choices=(("a", "A"),))
    activo = forms.BooleanField(required=False)
    archivo = forms.FileField(required=False)
    contenido = forms.CharField(widget=forms.Textarea)


class StyledFormTests(SimpleTestCase):
    def test_aplica_widgets_segun_tipo_de_campo(self):
        form = ExampleStyledForm()

        self.assertIsInstance(form.fields["nombre"].widget, FloatingInput)
        self.assertIsInstance(form.fields["email"].widget, FloatingEmailInput)
        self.assertIsInstance(form.fields["categoria"].widget, SelectInput)
        self.assertIsInstance(form.fields["activo"].widget, CheckboxInput)
        self.assertIsInstance(form.fields["archivo"].widget, FileInput)
        self.assertIsInstance(form.fields["contenido"].widget, QuillEditorWidget)

    def test_field_group_renderiza_etiqueta_errores_y_clases(self):
        form = ExampleStyledForm(data={})
        self.assertFalse(form.is_valid())

        html = form["nombre"].as_field_group()

        self.assertIn('class="form-control"', html)
        self.assertIn('for="id_nombre"', html)
        self.assertIn("Este campo es obligatorio", html)

    def test_quill_declara_recursos_locales(self):
        media = str(ExampleStyledForm().media)

        self.assertIn("vendor/libs/quill/quill.js", media)
        self.assertIn("core/js/quill-widgets.js", media)

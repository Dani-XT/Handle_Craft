from django import forms

from .widgets import (
    CheckboxInput,
    FileInput,
    FloatingDateInput,
    FloatingDateTimeInput,
    FloatingEmailInput,
    FloatingInput,
    FloatingNumberInput,
    FloatingPasswordInput,
    FloatingURLInput,
    QuillEditorWidget,
    SelectInput,
    SelectMultipleInput,
    TextAreaInput,
)


class StyledFieldsMixin:
    """Aplica el tema visual sin repetir widgets en cada formulario."""

    rich_text_fields = ()
    label_suffix = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            self._style_field(name, field)

    @staticmethod
    def _replace_widget(field, widget):
        widget.is_required = field.required
        widget.is_localized = field.localize
        field.widget = widget

    def _style_field(self, name, field):
        original = field.widget
        attrs = original.attrs.copy()

        if isinstance(original, forms.HiddenInput):
            return

        if name in self.rich_text_fields:
            self._replace_widget(field, QuillEditorWidget(attrs=attrs))
            field.template_name = "fields/quill_field.html"
            return

        if isinstance(original, forms.CheckboxInput):
            self._replace_widget(field, CheckboxInput(attrs=attrs, check_test=original.check_test))
            field.template_name = "fields/checkbox_field.html"
            return

        if isinstance(original, forms.ClearableFileInput):
            self._replace_widget(field, FileInput(attrs=attrs))
            field.template_name = "fields/file_field.html"
            return

        if isinstance(original, forms.SelectMultiple):
            self._replace_widget(field, SelectMultipleInput(attrs=attrs, choices=original.choices))
        elif isinstance(original, forms.Select):
            self._replace_widget(field, SelectInput(attrs=attrs, choices=original.choices))
        elif isinstance(original, forms.DateTimeInput):
            self._replace_widget(field, FloatingDateTimeInput(attrs=attrs, format=original.format))
        elif isinstance(original, forms.DateInput):
            self._replace_widget(field, FloatingDateInput(attrs=attrs, format=original.format))
        elif isinstance(original, forms.PasswordInput):
            self._replace_widget(field, FloatingPasswordInput(attrs=attrs, render_value=original.render_value))
        elif isinstance(original, forms.EmailInput):
            self._replace_widget(field, FloatingEmailInput(attrs=attrs))
        elif isinstance(original, forms.NumberInput):
            self._replace_widget(field, FloatingNumberInput(attrs=attrs))
        elif isinstance(original, forms.URLInput):
            self._replace_widget(field, FloatingURLInput(attrs=attrs))
        elif isinstance(original, forms.Textarea):
            self._replace_widget(field, TextAreaInput(attrs=attrs))
        elif isinstance(original, forms.TextInput):
            self._replace_widget(field, FloatingInput(attrs=attrs))
        else:
            classes = attrs.get("class", "").split()
            attrs["class"] = " ".join(dict.fromkeys([*classes, "form-control"]))
            original.attrs = attrs

        field.template_name = "fields/floating_field.html"


class StyledForm(StyledFieldsMixin, forms.Form):
    pass


class StyledModelForm(StyledFieldsMixin, forms.ModelForm):
    pass

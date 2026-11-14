from django import forms


def _classes(attrs, *names):
    """Devuelve attrs sin perder clases agregadas por un formulario concreto."""
    attrs = (attrs or {}).copy()
    current = attrs.get("class", "").split()
    attrs["class"] = " ".join(dict.fromkeys([*current, *names]))
    return attrs


class FloatingInput(forms.TextInput):
    template_name = "widgets/floating_input.html"

    def __init__(self, attrs=None):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        super().__init__(attrs=attrs)


class FloatingEmailInput(forms.EmailInput):
    template_name = "widgets/floating_input.html"

    def __init__(self, attrs=None):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        super().__init__(attrs=attrs)


class FloatingNumberInput(forms.NumberInput):
    template_name = "widgets/floating_input.html"

    def __init__(self, attrs=None):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        super().__init__(attrs=attrs)


class FloatingPasswordInput(forms.PasswordInput):
    template_name = "widgets/floating_input.html"

    def __init__(self, attrs=None, render_value=False):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        super().__init__(attrs=attrs, render_value=render_value)


class FloatingURLInput(forms.URLInput):
    template_name = "widgets/floating_input.html"

    def __init__(self, attrs=None):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        super().__init__(attrs=attrs)


class FloatingDateInput(forms.DateInput):
    input_type = "date"
    template_name = "widgets/floating_input.html"

    def __init__(self, attrs=None, format=None):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        super().__init__(attrs=attrs, format=format)


class FloatingDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"
    template_name = "widgets/floating_input.html"

    def __init__(self, attrs=None, format=None):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        super().__init__(attrs=attrs, format=format)


class TextAreaInput(forms.Textarea):
    template_name = "widgets/text_area.html"

    def __init__(self, attrs=None):
        attrs = _classes(attrs, "form-control")
        attrs.setdefault("placeholder", " ")
        attrs.setdefault("rows", 4)
        super().__init__(attrs=attrs)


class SelectInput(forms.Select):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs=_classes(attrs, "form-select"), choices=choices)


class SelectMultipleInput(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs=_classes(attrs, "form-select"), choices=choices)


class CheckboxInput(forms.CheckboxInput):
    def __init__(self, attrs=None, check_test=None):
        super().__init__(attrs=_classes(attrs, "form-check-input"), check_test=check_test)


class FileInput(forms.ClearableFileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs=_classes(attrs, "form-control"))


class QuillEditorWidget(forms.Textarea):
    """Editor opcional; debe habilitarse campo a campo en el formulario."""

    template_name = "widgets/quill_editor.html"

    def __init__(self, attrs=None):
        attrs = _classes(attrs, "d-none", "quill-source")
        super().__init__(attrs=attrs)

    def use_required_attribute(self, initial):
        return False

    class Media:
        css = {
            "all": (
                "vendor/libs/quill/typography.css",
                "vendor/libs/quill/katex.css",
                "vendor/libs/quill/editor.css",
            )
        }
        js = (
            "vendor/libs/quill/katex.js",
            "vendor/libs/quill/quill.js",
            "core/js/quill-widgets.js",
        )


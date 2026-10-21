from django.contrib import messages
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.core.exceptions import PermissionDenied

from django.contrib.auth import get_user_model

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from apps.acceso.technicians.forms.add_update import TechniciansAddUpdateForm

User = get_user_model()

class TechniciansAddUpdateView(PermissionRequiredMixin, FormView):
    raise_exception = True

    template_name = "technicians-add-update.html"
    form_class = TechniciansAddUpdateForm
    success_url = reverse_lazy("technicians-list")

    # Obtener usuario
    def get_object(self):
        if not hasattr(self, "_usuario"):
            pk = self.kwargs.get("pk")

            self._usuario = (
                get_object_or_404(User, pk=pk)
                if pk is not None
                else None
            )

        return self._usuario

    # Modificar permisos
    def get_permission_required(self):
        if self.get_object():
            return ("apps_auth.change_user",)

        return ("apps_auth.add_user",)

    # Mandar datos al formulario
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["actor"] = self.request.user
        usuario = self.get_object()

        if usuario:
            kwargs["instance"] = usuario

        return kwargs

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                "tecnico": self.get_object(),
            }
        )
        TemplateHelper.map_context(context)
        return context

    # Validacion formulario
    def form_valid(self, form):
        is_update = self.get_object() is not None

        try:
            usuario = form.save()
        except IntegrityError:
            accion = "modificar" if is_update else "crear"
            form.add_error(None, f"No fue posible {accion} el usuario porque sus datos ya existen.",)
            return self.form_invalid(form)

        accion = "modificado" if is_update else "creado"
        messages.success(self.request, f"Usuario {usuario.get_full_name()} {accion} correctamente.",)

        return super().form_valid(form)

    # Revisar si el formulario es valido
    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados antes de continuar.")
        return super().form_invalid(form)

    # Impedir modificacion propia
    def dispatch(self, request, *args, **kwargs):
        usuario_id = kwargs.get("pk")

        if (
            usuario_id is not None
            and request.user.is_authenticated
            and request.user.pk == usuario_id
        ):
            messages.warning(request, "Tu propia cuenta no puede modificarse desde la administración de técnicos.",)
            return redirect("home")

        return super().dispatch(request, *args, **kwargs)
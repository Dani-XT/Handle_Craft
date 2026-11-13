from django.contrib import messages
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from apps.inventario.categorias.forms.add_update import CategoriaInventarioAddUpdateForm

class CategoriaInventarioAddUpdateView(PermissionRequiredMixin, FormView):
    raise_exception = True

    template_name = "categorias-inventario-add-update.html"
    form_class = CategoriaInventarioAddUpdateForm
    success_url = reverse_lazy("categorias-inventario-list")

    # def get_object(self):
    #     if not hasattr(self, "_categoria"):
    #         pk = self.kwargs.get("pk")

    #         self._usuario = (
    #             get_object_or_404(User, pk=pk)
    #             if pk is not None
    #             else None
    #         )

    #     return self._usuario

    def get_permission_required(self):
        # if self.get_object():
        #     return ("apps_auth.change_user",)

        return ("apps_auth.add_user",)

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                # "tecnico": self.get_object(),
            }
        )
        TemplateHelper.map_context(context)
        return context

    def form_valid(self, form):
        print("hola")

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados antes de continuar.")
        return super().form_invalid(form)
    


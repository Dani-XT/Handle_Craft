from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.inventario.categorias.models import Categoria
from apps.inventario.categorias.forms.add_update import CategoriaInventarioAddUpdateForm


class CategoriaInventarioAddUpdateView(PermissionRequiredMixin, FormView):
    raise_exception = True
    template_name = "categorias-inventario-add-update.html"
    form_class = CategoriaInventarioAddUpdateForm
    success_url = reverse_lazy("categorias-inventario-list")

    def get_permission_required(self):
        accion = "change" if self.kwargs.get("pk") else "add"
        return (f"inventario_categorias.{accion}_categoria",)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.kwargs.get("pk"):
            kwargs["instance"] = get_object_or_404(Categoria.objects.internas(), pk=self.kwargs["pk"])
        return kwargs

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        TemplateHelper.map_context(context)
        return context

    def form_valid(self, form):
        categoria = form.save(commit=False)
        if not categoria.pk:
            categoria.created_by = self.request.user
        categoria.updated_by = self.request.user
        categoria.save()
        messages.success(self.request, "Categoría guardada.")
        return super().form_valid(form)

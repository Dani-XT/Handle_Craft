from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from apps.inventario.bodegas.forms.add import BodegasAddForm
from apps.inventario.bodegas.models import Bodega


class BodegasAddView(CreateView, PermissionRequiredMixin):
    permission_required = ("auth.view_user")
    raise_exception = True
    model = Bodega
    template_name = "bodegas-add-update.html"
    form_class = BodegasAddForm

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        TemplateHelper.map_context(context)
        return context

from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin

# from apps.activos.warehouse.forms.add_update import WarehouseAddUodateForm

class WarehouseAddUpdateView(PermissionRequiredMixin, FormView):
    raise_exception = True

    template_name = "warehouse-add-update.html"
    # form_class = WarehouseAddUodateForm
    success_url = reverse_lazy("warehouse-list")
    permission_required = ("apps_auth.add_user")


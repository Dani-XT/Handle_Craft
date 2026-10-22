from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from apps.acceso.users.forms.status import TechnicianStatusForm


User = get_user_model()


class TechnicianStatusView(PermissionRequiredMixin, View):
    permission_required = ("apps_auth.change_user",)
    raise_exception = True
    http_method_names = ["post"]

    @transaction.atomic
    def post(self, request, pk):
        tecnico = get_object_or_404(User.objects.select_for_update(), pk=pk)

        if tecnico.pk == request.user.pk:
            messages.error(request, "No puedes cambiar el estado de tu propia cuenta.",)
            return redirect("home")

        if (tecnico.is_superuser and not request.user.is_superuser):
            raise PermissionDenied("No tienes autorización para cambiar el estado de un superadministrador.")

        form = TechnicianStatusForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Debes confirmar el cambio de estado.",)
            return redirect("technicians-update", pk=tecnico.pk,)

        action = form.cleaned_data["action"]

        if (action == TechnicianStatusForm.ACTION_DEACTIVATE):
            nuevo_estado = False
            accion = "desactivada"
        else:
            nuevo_estado = True
            accion = "activada"

        if tecnico.is_active == nuevo_estado:
            messages.info(request, f"La cuenta ya se encuentra {accion}.")
        else:
            tecnico.is_active = nuevo_estado
            tecnico.save(update_fields=["is_active"])

            nombre = (tecnico.get_full_name() or tecnico.email)

            messages.success(request,f"La cuenta de {nombre} fue {accion} correctamente.",)

        return redirect("technicians-update", pk=tecnico.pk)
from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.acceso.permisos.views.views import PermisosListView

urlpatterns = [
    path(
        "permissions/list/",
        login_required(PermisosListView.as_view()),
        name = "permisos-list",
    ),
]
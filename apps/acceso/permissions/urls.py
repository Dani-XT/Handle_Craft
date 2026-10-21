from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.acceso.permissions.views.views import PermissionsListView

urlpatterns = [
    path(
        "permissions/list/",
        login_required(PermissionsListView.as_view()),
        name = "permissions-list",
    ),
]
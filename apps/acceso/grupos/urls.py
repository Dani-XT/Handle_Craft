from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.acceso.grupos.views.views import GruposListView
from apps.acceso.grupos.views.add_update import GruposAddUpdateView

urlpatterns = [
    path(
        "groups/list/",
        login_required(GruposListView.as_view()),
        name = "grupos-list"
    ),
    path(
        "groups/add/",
        login_required(GruposAddUpdateView.as_view()),
        name = "grupos-add"
    ),
]
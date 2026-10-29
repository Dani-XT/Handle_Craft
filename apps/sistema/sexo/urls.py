from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.sistema.sexo.views.views import SexoListView

urlpatterns = [
    path(
        "sex/list/",
        login_required(SexoListView.as_view()),
        name = "sexo-list",
    ),
]
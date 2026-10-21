from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.actas.clients.views.views import ClientsListView

urlpatterns = [
    path(
        "clients/list/",
        login_required(ClientsListView.as_view()),
        name = "clients-list",
    ),
]
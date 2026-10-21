from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.activos.computers.views.views import ComputersListsView

urlpatterns = [
    path(
        "computers/list/",
        login_required(ComputersListsView.as_view()),
        name = "computers-list",
    ),
]
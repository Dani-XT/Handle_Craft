from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.trabajadores.personas.views.views import PersonasListView

urlpatterns = [
    path(
        "persons/list/",
        login_required(PersonasListView.as_view()),
        name = "personas-list"
    ),
]
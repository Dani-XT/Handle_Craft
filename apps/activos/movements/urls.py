from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.activos.movements.views.views import MovementsListView

urlpatterns = [
    path(
        "movements/list/",
        login_required(MovementsListView.as_view()),
        name = "movements-list",
    ),
]
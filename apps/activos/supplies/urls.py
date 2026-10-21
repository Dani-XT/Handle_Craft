from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.activos.supplies.views.views import SuppliesListView

urlpatterns = [
    path(
        "supplies/list/",
        login_required(SuppliesListView.as_view()),
        name = "supplies-list",
    ),
]
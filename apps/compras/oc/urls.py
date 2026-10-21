from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.compras.providers.views.views import ProvidersListView

urlpatterns = [
    path(
        "providers/list/",
        login_required(ProvidersListView.as_view()),
        name = "providers-list",
    ),
]
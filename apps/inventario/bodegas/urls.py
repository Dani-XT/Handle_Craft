from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.inventario.bodegas.views.views import BodegasListView

urlpatterns = [
    path(
        "warehouse/list/",
        login_required(BodegasListView.as_view()),
        name = "bodegas-list"
    ),
]
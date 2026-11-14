from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.inventario.bodegas.views.views import BodegasListView
from apps.inventario.bodegas.views.add import BodegasAddView

urlpatterns = [
    path(
        "warehouse/list/",
        login_required(BodegasListView.as_view()),
        name = "bodegas-list"
    ),
    path(
        "warehouse/add/",
        login_required(BodegasAddView.as_view()),
        name = "bodegas-add"
    ),
]
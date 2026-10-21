from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.activos.warehouse.views.views import WarehouseListView

urlpatterns = [
    path(
        "warehouse/list/",
        login_required(WarehouseListView.as_view()),
        name = "warehouse-list",
    ),
]
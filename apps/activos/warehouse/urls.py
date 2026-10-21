from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.activos.warehouse.views.views import WarehouseListView
from apps.activos.warehouse.views.add_update import WarehouseAddUpdateView

urlpatterns = [
    path(
        "warehouse/list/",
        login_required(WarehouseListView.as_view()),
        name = "warehouse-list",
    ),
    path(
        "warehouse/add/",
        login_required(WarehouseAddUpdateView.as_view()),
        name = "warehouse-add"
    ),
    path(
        "warehouse/update/<int:pk>/",
        login_required(WarehouseAddUpdateView.as_view()),
        name = "warehouse-update"
    ),
]
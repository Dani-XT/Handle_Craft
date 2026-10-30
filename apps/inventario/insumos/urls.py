from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.inventario.insumos.views.views import InsumosListView

urlpatterns = [
    path(
        "supplies/list/",
        login_required(InsumosListView.as_view()),
        name = "insumos-list"
    ),
]
from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.trabajadores.areas.views.views import AreasListView

urlpatterns = [
    path(
        "products/list/",
        login_required(AreasListView.as_view()),
        name = "areas-list"
    ),
]
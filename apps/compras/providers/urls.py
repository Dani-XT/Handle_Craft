from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.compras.oc.views.views import OcListView

urlpatterns = [
    path(
        "oc/list/",
        login_required(OcListView.as_view()),
        name = "oc-list",
    ),
]
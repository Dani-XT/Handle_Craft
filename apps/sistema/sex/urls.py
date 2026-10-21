from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.sistema.sex.views.views import SexListView

urlpatterns = [
    path(
        "sex/list/",
        login_required(SexListView.as_view()),
        name = "sex-list",
    ),
]
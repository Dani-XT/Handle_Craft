from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.acceso.usuarios.views.views import UsersListView
from apps.acceso.usuarios.views.add_update import UsersAddUpdateView

urlpatterns = [
    path(
        "users/list/",
        login_required(UsersListView.as_view()),
        name = "usuarios-list"
    ),
    path(
        "users/add/",
        login_required(UsersAddUpdateView.as_view()),
        name = "usuarios-add"
    ),
    path(
        "users/update/<int:pk>/",
        login_required(UsersAddUpdateView.as_view()),
        name = "usuarios-update",
    ),
]
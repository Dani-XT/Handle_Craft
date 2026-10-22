from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.acceso.users.views.views import UsersListView
from apps.acceso.users.views.add_update import UsersAddUpdateView

from apps.acceso.users.views.status import TechnicianStatusView

urlpatterns = [
    path(
        "users/list/",
        login_required(UsersListView.as_view()),
        name = "users-list"
    ),
    path(
        "users/add/",
        login_required(UsersAddUpdateView.as_view()),
        name = "users-add"
    ),
    path(
        "users/update/<int:pk>/",
        login_required(UsersAddUpdateView.as_view()),
        name = "users-update",
    ),
    path(
        "users/<int:pk>/status/",
        login_required(TechnicianStatusView.as_view()),
        name="users-status",
    ),
]
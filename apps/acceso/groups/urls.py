from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.acceso.groups.views.views import GroupsListView
from apps.acceso.groups.views.add_update import GroupsAddUpdateView

urlpatterns = [
    path(
        "groups/list/",
        login_required(GroupsListView.as_view()),
        name = "groups-list"
    ),
    path(
        "groups/add/",
        login_required(GroupsAddUpdateView.as_view()),
        name = "groups-add"
    ),
]
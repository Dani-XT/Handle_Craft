from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.actas.locations.views.views import LocationsListView

urlpatterns = [
    path(
        "locations/list/",
        login_required(LocationsListView.as_view()),
        name = "locations-list",
    ),
]
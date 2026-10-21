from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.ETL.etl.views.views import ETLMainView

urlpatterns = [
    path(
        "etl/",
        login_required(ETLMainView.as_view()),
        name = "etl-main",
    ),
]
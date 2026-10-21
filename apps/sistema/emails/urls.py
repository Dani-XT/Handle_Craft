from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.sistema.emails.views.views import EmailsListView

urlpatterns = [
    path(
        "emails/list/",
        login_required(EmailsListView.as_view()),
        name = "emails-list",
    ),
]
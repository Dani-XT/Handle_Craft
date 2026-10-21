from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.automation.automation.views.views import AutomationMainView

urlpatterns = [
    path(
        "automation/",
        login_required(AutomationMainView.as_view()),
        name = "automation-main",
    ),
]
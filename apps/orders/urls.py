from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.orders.views.views import OrdersListView

urlpatterns = [
    path(
        "orders/list/",
        login_required(OrdersListView.as_view()),
        name = "orders-list",
    ),
]
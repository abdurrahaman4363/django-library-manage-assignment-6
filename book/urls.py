from django.urls import path
from . import views


urlpatterns = [
    path("details/<int:id>", views.DetailBookView.as_view(), name="details_book"),
    # path("purchase_car/<int:id>", views.purchase_car, name="purchase_car"),
]

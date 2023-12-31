from django.urls import path
from .views import DepositeMoneyView, TransactionReportView, BorrowBookView


urlpatterns = [
    path("deposite/", DepositeMoneyView.as_view(), name="deposite_money"),
    path("report/", TransactionReportView.as_view(), name="transaction_report"),
    path("borrow/", BorrowBookView.as_view(), name="borrow_book"),
]

from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm, BorrowForm
from .constants import DEPOSITE, BORROWING_BOOK
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from accounts.models import UserLibraryAccount, BorrowingHistory
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

# Create your views here.


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = "transaction_form.html"
    model = Transaction
    title = ""
    success_url = reverse_lazy("transaction_report")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "account": self.request.user.account,
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update(
            {
                "title": self.title,
            }
        )
        return context


class DepositeMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = "Deposite"

    def get_initial(self):
        initial = {"transaction_type": DEPOSITE}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        account.balance += amount
        account.save(update_fields=["balance"])

        messages.success(
            self.request, f"{amount}$ was deposited to your account successfully"
        )

        mail_subject = "Deposite Message"
        message = render_to_string(
            "deposite_mail.html", {"user": self.request.user, "amount": amount}
        )
        to_email = self.request.user.email
        send_email = EmailMultiAlternatives(mail_subject, "", to=[to_email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()
        return super().form_valid(form)


class BorrowBookView(TransactionCreateMixin):
    form_class = BorrowForm
    title = "Borrow Book"

    def get_initial(self):
        initial = {"transaction_type": BORROWING_BOOK}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        account.balance -= amount
        account.save(update_fields=["balance"])

        messages.success(self.request, f"You have successfully borrowed Book")
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "accounts/profile.html"
    model = Transaction
    balance = 0
    context_object_name = "report_list"

    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            )
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum("amount"))["amount__sum"]
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"account": self.request.user.account})

        return context

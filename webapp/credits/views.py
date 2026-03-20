from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Credit


@login_required
def index(request):
    account = request.user.account
    balance = account.balance
    has_active_loan = Credit.objects.filter(
        user=request.user,
        is_active=True
    ).exists()

    return render(request, 'credits/index.html', {
        'has_active_loan': has_active_loan,
        'balance': balance,
    })

@login_required
def pay_extra(request):
    has_active_loan = Credit.objects.filter(
        user=request.user,
        is_active=True
    ).exists()

    return render(request, 'credits/pay_extra.html', {
        'has_active_loan': has_active_loan,
    })

@login_required
def avaible_loans(request):
    has_active_loan = Credit.objects.filter(
        user=request.user,
        is_active=True
    ).exists()

    return render(request, 'credits/avaible_loans.html', {
        'has_active_loan': has_active_loan,
    })

@login_required
def mortgage(request):
    has_mortgage = Credit.objects.filter(
        user=request.user,
        is_active=True
    ).exists()

    return render(request, 'credits/mortgage.html', {
        'has_mortgage': has_mortgage,
    })
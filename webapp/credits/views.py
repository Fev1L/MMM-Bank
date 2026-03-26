from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Credit
from main.models import Category, Transaction


@login_required
def index(request):
    account = request.user.account
    balance = account.balance
    active_credits = Credit.objects.filter(
        user=request.user,
        is_active=True
    )

    return render(request, 'credits/index.html', {
        'has_active_loan': active_credits.exists(),
        'balance': balance,
    })

@login_required
def pay_extra(request):
    loans = Credit.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('created_at')

    if request.method == 'POST':
        loan = get_object_or_404(loans, id=request.POST.get('loan'))

        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except InvalidOperation:
            amount = Decimal('0')

        if amount <= 0:
            messages.error(request, 'Enter a valid amount greater than 0.')
            return redirect('pay_extra')

        if amount > loan.amount:
            messages.error(request, 'Extra payment cannot be bigger than the remaining loan balance.')
            return redirect('pay_extra')

        payment_category, _ = Category.objects.get_or_create(
            name='Loan payment',
            type=Category.WITHDRAW
        )

        try:
            with db_transaction.atomic():
                Transaction.objects.create(
                    account=request.user.account,
                    amount=amount,
                    category=payment_category,
                    title=f'Extra payment for {loan.client_name}'
                )

                loan.amount -= amount
                if loan.amount == 0:
                    loan.is_active = False
                loan.save(update_fields=['amount', 'is_active'])
        except ValidationError as exc:
            messages.error(request, str(exc))
            return redirect('pay_extra')

        if loan.is_active:
            messages.success(request, f'Extra payment of ${amount} was applied to {loan.client_name}.')
        else:
            messages.success(request, f'{loan.client_name} has been fully repaid.')
        return redirect('pay_extra')

    return render(request, 'credits/pay_extra.html', {
        'has_active_loan': loans.exists(),
        'loans': loans,
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
        is_active=True,
        client_name='Mortgage',
    ).exists()

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except InvalidOperation:
            amount = Decimal('0')

        years_raw = request.POST.get('years', '0')
        try:
            years = int(years_raw)
        except (TypeError, ValueError):
            years = 0

        if has_mortgage:
            messages.error(request, 'You already have an active mortgage.')
            return redirect('mortgage')

        if amount <= 0 or amount > Decimal('100000'):
            messages.error(request, 'Mortgage amount must be between $1 and $100000.')
            return redirect('mortgage')

        if years < 1 or years > 30:
            messages.error(request, 'Mortgage term must be between 1 and 30 years.')
            return redirect('mortgage')

        mortgage_category, _ = Category.objects.get_or_create(
            name='Mortgage payout',
            type=Category.DEPOSIT
        )

        with db_transaction.atomic():
            credit = Credit.objects.create(
                user=request.user,
                client_name='Mortgage',
                amount=amount,
                interest_rate=3.5,
                is_active=True,
            )

            Transaction.objects.create(
                account=request.user.account,
                amount=amount,
                category=mortgage_category,
                title=f'Mortgage approved: {credit.client_name}'
            )

        messages.success(request, 'Mortgage application approved and credited to your account.')
        return redirect('mortgage')

    return render(request, 'credits/mortgage.html', {
        'has_mortgage': has_mortgage,
    })

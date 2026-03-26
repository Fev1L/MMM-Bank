from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Credit
from main.models import Category, Transaction


AVAILABLE_LOANS = [
    {
        'key': 'bicycle',
        'client_name': 'Bicycle loan',
        'amount': Decimal('500.00'),
        'interest_rate': 5.0,
        'gradient': 'linear-gradient(90deg,#5b3df5,#8a7be0)',
    },
    {
        'key': 'motorcycle',
        'client_name': 'Motorcycle loan',
        'amount': Decimal('3000.00'),
        'interest_rate': 4.5,
        'gradient': 'linear-gradient(90deg,#4b2fd6,#7c6ce0)',
    },
    {
        'key': 'car',
        'client_name': 'Car loan',
        'amount': Decimal('20000.00'),
        'interest_rate': 3.5,
        'gradient': 'linear-gradient(90deg,#3c25b8,#6e5de0)',
    },
    {
        'key': 'apartment',
        'client_name': 'Apartment loan',
        'amount': Decimal('50000.00'),
        'interest_rate': 2.8,
        'gradient': 'linear-gradient(90deg,#2d1ea8,#5f4fe0)',
    },
    {
        'key': 'house',
        'client_name': 'House loan',
        'amount': Decimal('100000.00'),
        'interest_rate': 2.3,
        'gradient': 'linear-gradient(90deg,#25198f,#5647d9)',
    },
]


@login_required
def index(request):
    account = request.user.account
    balance = account.balance
    show_all_activity = request.GET.get('activity') == 'all'
    show_all_cards = request.GET.get('cards') == 'all'
    active_credits = Credit.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-created_at')
    loan_activity_queryset = Transaction.objects.filter(
        account=account
    ).filter(
        Q(title__startswith='Loan approved:')
        | Q(title__startswith='Extra payment for')
        | Q(title__startswith='Mortgage approved:')
    ).select_related('category').order_by('-created_at')
    loan_activity = loan_activity_queryset if show_all_activity else loan_activity_queryset[:4]
    active_credit_cards = []
    credits_for_cards = active_credits if show_all_cards else active_credits[:2]
    for credit in credits_for_cards:
        estimated_monthly = (credit.amount * Decimal(str(1 + credit.interest_rate / 100))) / Decimal('12')
        active_credit_cards.append({
            'title': credit.client_name,
            'amount': credit.amount,
            'left': credit.amount,
            'monthly': estimated_monthly.quantize(Decimal('0.01')),
            'rate': credit.interest_rate,
            'status': 'Active' if credit.is_active else 'Closed',
            'is_placeholder': False,
        })
    if not active_credit_cards:
        active_credit_cards = [
            {
                'title': 'No active loans yet',
                'amount': Decimal('0.00'),
                'left': Decimal('0.00'),
                'monthly': Decimal('0.00'),
                'rate': Decimal('0.00'),
                'status': 'Waiting for application',
                'is_placeholder': True,
            },
            {
                'title': 'No active loans yet',
                'amount': Decimal('0.00'),
                'left': Decimal('0.00'),
                'monthly': Decimal('0.00'),
                'rate': Decimal('0.00'),
                'status': 'Waiting for application',
                'is_placeholder': True,
            },
        ]

    return render(request, 'credits/index.html', {
        'has_active_loan': active_credits.exists(),
        'balance': balance,
        'loan_activity': loan_activity,
        'show_all_activity': show_all_activity,
        'active_credit_cards': active_credit_cards,
        'show_all_cards': show_all_cards,
        'has_more_credit_cards': active_credits.count() > 2,
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
    active_loans = Credit.objects.filter(
        user=request.user,
        is_active=True
    )

    if request.method == 'POST':
        loan_key = request.POST.get('loan_type')
        loan_data = next((loan for loan in AVAILABLE_LOANS if loan['key'] == loan_key), None)

        if loan_data is None:
            messages.error(request, 'Please choose a valid loan option.')
            return redirect('avaible_loans')

        payout_category, _ = Category.objects.get_or_create(
            name='Loan payout',
            type=Category.DEPOSIT
        )

        with db_transaction.atomic():
            credit = Credit.objects.create(
                user=request.user,
                client_name=loan_data['client_name'],
                amount=loan_data['amount'],
                interest_rate=loan_data['interest_rate'],
                is_active=True,
            )

            Transaction.objects.create(
                account=request.user.account,
                amount=loan_data['amount'],
                category=payout_category,
                title=f"Loan approved: {credit.client_name}"
            )

        messages.success(request, f"{loan_data['client_name']} was added to your account.")
        return redirect('avaible_loans')

    return render(request, 'credits/avaible_loans.html', {
        'has_active_loan': active_loans.exists(),
        'loan_options': AVAILABLE_LOANS,
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

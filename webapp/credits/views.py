from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Credit
from main.models import Category, InboxMessage, Transaction


MAX_LOAN_LIMIT = Decimal('200000.00')
DEFAULT_LOAN_INTEREST = 4.0


def get_active_credit_total(user):
    active_credits = Credit.objects.filter(user=user, is_active=True)
    return sum((credit.amount for credit in active_credits), Decimal('0.00'))


def create_credit_notification(user, title, content):
    InboxMessage.objects.create(
        receiver=user,
        title=title,
        content=content,
        type=InboxMessage.SYSTEM,
    )


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
    return render(request, 'credits/index.html', {
        'has_active_loan': active_credits.exists(),
        'balance': balance,
        'loan_activity': loan_activity,
        'show_all_activity': show_all_activity,
        'active_credit_cards': active_credit_cards,
        'has_active_credit_cards': bool(active_credit_cards),
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
            create_credit_notification(
                request.user,
                'Credit payment declined',
                'Enter a valid extra payment amount greater than 0.',
            )
            return redirect('pay_extra')

        if amount > loan.amount:
            create_credit_notification(
                request.user,
                'Credit payment declined',
                'Extra payment cannot be bigger than the remaining loan balance.',
            )
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
            create_credit_notification(
                request.user,
                'Credit payment declined',
                str(exc),
            )
            return redirect('pay_extra')

        if loan.is_active:
            create_credit_notification(
                request.user,
                'Credit payment received',
                f'Extra payment of ${amount} was applied to {loan.client_name}.',
            )
        else:
            create_credit_notification(
                request.user,
                'Credit closed',
                f'{loan.client_name} has been fully repaid.',
            )
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
        loan_target = request.POST.get('loan_target', '').strip()

        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except InvalidOperation:
            amount = Decimal('0')

        if not loan_target:
            create_credit_notification(
                request.user,
                'Credit request declined',
                'Please enter what you want to take the credit for.',
            )
            return redirect('avaible_loans')

        if amount <= 0:
            create_credit_notification(
                request.user,
                'Credit request declined',
                'Please enter a valid loan amount.',
            )
            return redirect('avaible_loans')

        if amount > MAX_LOAN_LIMIT:
            create_credit_notification(
                request.user,
                'Credit request declined',
                'You cannot take a loan for this amount. Maximum loan limit is $200000.',
            )
            return redirect('avaible_loans')

        current_total = get_active_credit_total(request.user)
        if current_total >= MAX_LOAN_LIMIT or current_total + amount > MAX_LOAN_LIMIT:
            create_credit_notification(
                request.user,
                'Credit limit reached',
                'You have reached the credit limit. Return the debt first.',
            )
            return redirect('avaible_loans')

        payout_category, _ = Category.objects.get_or_create(
            name='Loan payout',
            type=Category.DEPOSIT
        )

        with db_transaction.atomic():
            credit = Credit.objects.create(
                user=request.user,
                client_name=f'{loan_target.title()} loan',
                amount=amount,
                interest_rate=DEFAULT_LOAN_INTEREST,
                is_active=True,
            )

            Transaction.objects.create(
                account=request.user.account,
                amount=amount,
                category=payout_category,
                title=f"Loan approved: {credit.client_name}"
            )

        create_credit_notification(
            request.user,
            'Credit approved',
            f'{credit.client_name} was added to your account for ${amount}.',
        )
        return redirect('avaible_loans')

    return render(request, 'credits/avaible_loans.html', {
        'has_active_loan': active_loans.exists(),
        'max_loan_limit': MAX_LOAN_LIMIT,
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
            create_credit_notification(
                request.user,
                'Mortgage request declined',
                'You already have an active mortgage.',
            )
            return redirect('mortgage')

        if amount <= 0 or amount > Decimal('100000'):
            create_credit_notification(
                request.user,
                'Mortgage request declined',
                'Mortgage amount must be between $1 and $100000.',
            )
            return redirect('mortgage')

        current_total = get_active_credit_total(request.user)
        if current_total >= MAX_LOAN_LIMIT or current_total + amount > MAX_LOAN_LIMIT:
            create_credit_notification(
                request.user,
                'Credit limit reached',
                'You have reached the credit limit. Return the debt first.',
            )
            return redirect('mortgage')

        if years < 1 or years > 30:
            create_credit_notification(
                request.user,
                'Mortgage request declined',
                'Mortgage term must be between 1 and 30 years.',
            )
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

        create_credit_notification(
            request.user,
            'Mortgage approved',
            f'Mortgage application approved and credited to your account for ${amount}.',
        )
        return redirect('mortgage')

    return render(request, 'credits/mortgage.html', {
        'has_mortgage': has_mortgage,
    })

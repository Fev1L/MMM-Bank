import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from credits.models import Credit, Account , Category, Transaction

MAX_LOAN_LIMIT = Decimal('200000.00')
DEFAULT_LOAN_INTEREST = 4.0

@csrf_exempt
def api_credits(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        active_credits = Credit.objects.filter(user=request.user, is_active=True).order_by('-created_at')
        credits_data = [{
            'id': c.id,
            'title': c.title,
            'amount': str(c.amount),
            'rate': c.interest_rate,
            'currency': c.account.currency_type.code if c.account else 'USD',
            'created_at': c.created_at.isoformat()
        } for c in active_credits]

        return JsonResponse({'credits': credits_data})

    elif request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(str(data.get('amount', 0)))
        loan_target = data.get('loan_target', '').strip()
        currency = data.get('currency')

        if amount <= 0 or not loan_target or not currency:
            return JsonResponse({'message': 'Please fill in all the fields correctly'}, status=400)

        current_total = sum(c.amount for c in Credit.objects.filter(user=request.user, is_active=True))
        if current_total + amount > MAX_LOAN_LIMIT:
            return JsonResponse({'message': f'The credit limit has been exceeded. Maximum: {MAX_LOAN_LIMIT}'}, status=400)

        try:
            account = Account.objects.get(user=request.user, currency_type__code=currency)
            payout_category, _ = Category.objects.get_or_create(name='Loan payout', type=Category.DEPOSIT)

            with transaction.atomic():
                credit = Credit.objects.create(
                    user=request.user,
                    title=loan_target,
                    account=account,
                    amount=amount,
                    interest_rate=DEFAULT_LOAN_INTEREST,
                    is_active=True,
                )
                Transaction.objects.create(
                    account=account,
                    amount=amount,
                    category=payout_category,
                    transaction_type=Category.DEPOSIT,
                    title=f"Loan approved: {credit.user.first_name} {credit.user.last_name}",
                )

            return JsonResponse({'message': f'The loan for {amount} has been approved!'})

        except Account.DoesNotExist:
            return JsonResponse({'message': 'Account not found'}, status=404)
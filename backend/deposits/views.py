from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import PiggyBank, Deposit
from main.models import Transaction, Category, Account

@csrf_exempt
def api_piggy_bank(request):
    if request.method == 'GET':
        piggies = PiggyBank.objects.filter(user=request.user).order_by('-created_at')

        data = []
        for p in piggies:
            percent = min(int((p.balance / p.goal) * 100), 100) if p.goal > 0 else 0
            data.append({
                "id": p.id,
                "name": p.name,
                "balance": p.balance,
                "goal": p.goal,
                "percent": percent,
            })
        return JsonResponse({"piggies": data})

    elif request.method == 'POST':
        action = request.data.get("action")

        if action == "create":
            name = request.data.get("name", "My Piggy Bank").strip()
            goal = Decimal(str(request.data.get('goal', '0')))
            PiggyBank.objects.create(user=request.user, name=name, balance=Decimal('0'), goal=goal)
            return JsonResponse({"message": "Piggy Bank created successfully!"})

        elif action in ["add", "withdraw"]:
            piggy_id = request.data.get("piggy_id")
            amount = Decimal(str(request.data.get("amount", 0)))
            account_currency = request.data.get("currency")

            if amount <= 0:
                return JsonResponse({"message": "Amount must be greater than zero."}, status=400)

            try:
                piggy = PiggyBank.objects.get(id=piggy_id, user=request.user)
                account = Account.objects.get(user=request.user, currency_type__code=account_currency)

                cat_add, _ = Category.objects.get_or_create(name="To Piggy Bank", type=Category.WITHDRAW)
                cat_withdraw, _ = Category.objects.get_or_create(name="From Piggy Bank", type=Category.DEPOSIT)

                with transaction.atomic():
                    if action == "add":
                        if account.balance < amount:
                            return JsonResponse({"message": "Not enough funds on account."}, status=400)

                        account.balance -= amount
                        piggy.balance += amount

                        Transaction.objects.create(
                            account=account, amount=amount, category=cat_add,
                            transaction_type=Category.WITHDRAW, title=f"Saved to {piggy.name}"
                        )

                    elif action == "withdraw":
                        if piggy.balance < amount:
                            return JsonResponse({"message": "Not enough funds in Piggy Bank."}, status=400)

                        piggy.balance -= amount
                        account.balance += amount

                        Transaction.objects.create(
                            account=account, amount=amount, category=cat_withdraw,
                            transaction_type=Category.DEPOSIT, title=f"Withdrawn from {piggy.name}"
                        )

                    account.save()
                    piggy.save()

                return JsonResponse({"message": f"Successfully {action}ed {amount} {account_currency}!"})

            except Account.DoesNotExist:
                return JsonResponse({"message": "Account not found."}, status=404)
            except PiggyBank.DoesNotExist:
                return JsonResponse({"message": "Piggy Bank not found."}, status=404)
            except Exception as e:
                return JsonResponse({"message": str(e)}, status=500)

@csrf_exempt
def api_deposits_list(request):
    deposits = Deposit.objects.filter(user=request.user, is_active=True)
    history = Deposit.objects.filter(user=request.user, is_active=False)

    def serialize(deps):
        return [{
            "id": d.id, "amount": d.amount, "rate": d.rate,
            "duration": d.duration, "profit": d.profit(),
            "created_at": d.created_at
        } for d in deps]

    return JsonResponse({
        "active_deposits": serialize(deposits),
        "history": serialize(history)
    })

@csrf_exempt
def api_open_deposit(request):
    data = request.data
    amount = Decimal(str(data.get("amount", 0)))
    duration = int(data.get("duration", 0))
    currency = data.get("currency")

    if amount <= 0:
        return JsonResponse({"message": "Invalid amount."}, status=400)

    rates = {3: 3, 6: 5, 12: 7, 24: 9}
    rate = rates.get(duration, 5)

    try:
        account = Account.objects.get(user=request.user, currency_type__code=currency)

        if account.balance < amount:
            return JsonResponse({"message": "Not enough funds."}, status=400)

        with transaction.atomic():
            account.balance -= amount
            account.save()

            transfer_category, _ = Category.objects.get_or_create(name="Open Deposit", type=Category.WITHDRAW)
            Transaction.objects.create(
                account=account, amount=amount, category=transfer_category,
                transaction_type=Category.WITHDRAW, title="Deposit opened"
            )

            Deposit.objects.create(user=request.user, amount=amount, duration=duration, rate=rate)

        return JsonResponse({"message": "Deposit opened successfully!"})

    except Account.DoesNotExist:
        return JsonResponse({"message": "Account not found."}, status=404)
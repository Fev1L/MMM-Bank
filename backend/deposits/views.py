import json
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from .models import PiggyBank, Deposit
from main.models import Transaction, Category, Account
from main.views import get_real_rates

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_piggy_bank(request):
    if request.method == 'GET':
        piggies = PiggyBank.objects.filter(user=request.user).order_by('-created_at')

        data = []
        for p in piggies:
            percent = min(int((p.balance / p.goal) * 100), 100) if p.goal > 0 else 0
            currency = p.account.currency_type_id
            data.append({
                "id": p.id,
                "name": p.name,
                "balance": p.balance,
                "goal": p.goal,
                "percent": percent,
                "currency": currency,
            })
        return JsonResponse({"piggies": data})

    elif request.method == 'POST':
        data = json.loads(request.body)
        action = data.get("action")

        if action == "create":
            name = data.get("name", "My Piggy Bank").strip()
            goal = Decimal(str(data.get('goal', '0')))
            account_currency = data.get("currency")
            account = Account.objects.get(user=request.user, currency_type__code=account_currency)

            PiggyBank.objects.create(user=request.user, name=name, balance=Decimal('0'), account=account, goal=goal)
            return JsonResponse({"message": "Piggy Bank created successfully!"})

        elif action in ["add", "withdraw"]:
            piggy_id = data.get("piggy_id")
            amount = Decimal(str(data.get("amount", 0)))
            account_currency = data.get("currency")
            pay_amount = amount

            if amount <= 0:
                return JsonResponse({"message": "Amount must be greater than zero."}, status=400)

            try:
                piggy = PiggyBank.objects.get(id=piggy_id, user=request.user)
                account = Account.objects.get(user=request.user, currency_type__code=account_currency)

                cat_add, _ = Category.objects.get_or_create(name="To Piggy Bank", type=Category.WITHDRAW)
                cat_withdraw, _ = Category.objects.get_or_create(name="From Piggy Bank", type=Category.DEPOSIT)

                if piggy.account.currency_type.code != account_currency:
                    rates = get_real_rates()

                    if piggy.account.currency_type.code not in rates or account_currency not in rates:
                        return JsonResponse({'status': 'error', 'message': 'A currency conversion error has occurred on the server. Please try again later.'}, status=500)

                    rate_sender = Decimal(str(rates[account_currency]))
                    rate_receiver = Decimal(str(rates[piggy.account.currency_type.code]))

                    pay_amount = (amount / rate_sender) * rate_receiver
                    pay_amount = pay_amount.quantize(Decimal('0.01'))

                with transaction.atomic():
                    if action == "add":
                        if account.balance < pay_amount:
                            return JsonResponse({"message": "Not enough funds on account."}, status=400)

                        piggy.balance += pay_amount

                        Transaction.objects.create(
                            account=account, amount=pay_amount, category=cat_add,
                            transaction_type=Category.WITHDRAW, title=f"Saved to {piggy.name}"
                        )

                    elif action == "withdraw":
                        if piggy.balance < pay_amount:
                            return JsonResponse({"message": "Not enough funds in Piggy Bank."}, status=400)

                        piggy.balance -= pay_amount

                        Transaction.objects.create(
                            account=account, amount=pay_amount, category=cat_withdraw,
                            transaction_type=Category.DEPOSIT, title=f"Withdrawn from {piggy.name}"
                        )

                    account.save()
                    piggy.save()

                return JsonResponse({"message": f"Successfully {action}ed {pay_amount} {account_currency}!"})

            except Account.DoesNotExist:
                return JsonResponse({"message": "Account not found."}, status=404)
            except PiggyBank.DoesNotExist:
                return JsonResponse({"message": "Piggy Bank not found."}, status=404)
            except Exception as e:
                return JsonResponse({"message": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_deposits_list(request):
    deposits = Deposit.objects.filter(user=request.user)

    data = []
    for d in deposits:
        currency = d.account.currency_type_id
        data.append({
            "id": d.id,
            "amount": d.amount,
            "rate": d.rate,
            "duration": d.duration,
            "profit": d.profit(),
            "created_at": d.created_at,
            "currency": currency
        })
    return JsonResponse({"active_deposits": data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_open_deposit(request):
    data = json.loads(request.body)
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
            transfer_category, _ = Category.objects.get_or_create(name="Open Deposit", type=Category.WITHDRAW)
            Transaction.objects.create(
                account=account, amount=amount, category=transfer_category,
                transaction_type=Category.WITHDRAW, title="Deposit opened"
            )
            Transaction.objects.create(
                account=account, amount=amount, category=transfer_category,
                transaction_type=Category.WITHDRAW, title="Deposit opened"
            )
            send_mail(
                subject="New Deposit Opened - MMMBank",
                message=f"Your deposit for {amount}  has been opened.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
                html_message=f"""
                            <div style="font-family: Arial, sans-serif; background-color:#f4f6f8; padding:20px;">
                                <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; overflow:hidden; box-shadow:0 6px 16px rgba(0,0,0,0.1);">

                                    <div style="background: linear-gradient(135deg, #7b2cbf, #5a189a); color:white; padding:30px 20px; text-align:center;">
                                        <h2 style="margin:0; font-size: 24px; letter-spacing: 1px;">MMMBank</h2>
                                        <p style="margin:5px 0 0; opacity: 0.9; font-size: 14px;">Trusted Financial Services</p>
                                    </div>

                                    <div style="padding:40px 30px;">
                                        <h3 style="color:#333; font-size: 20px; margin-top: 0;">Deposit Opened 📈</h3>

                                        <p style="color:#555; line-height: 1.5;">
                                            Dear {request.user.username},
                                        </p>

                                        <p style="color:#555; line-height: 1.5;">
                                            We are pleased to confirm that your new deposit has been successfully opened and is now active.
                                        </p>

                                        <div style="background:#f3e8ff; padding:20px; border-radius:12px; margin:25px 0; border-left:5px solid #7b2cbf;">
                                            <p style="margin: 0 0 10px 0; color: #333;">
                                                <span style="font-size: 18px;">💰</span> <strong>Amount:</strong> {amount}
                                            </p>
                                            <p style="margin: 0 0 10px 0; color: #333;">
                                                
                                            </p>
                                            <p style="margin: 0 0 10px 0; color: #333;">
                                                <strong>Interest Rate:</strong> {rate}% APR
                                            </p>
                                            <p style="margin: 0; color: #333;">
                                                <strong>Status:</strong> Active
                                            </p>
                                        </div>

                                        <p style="color:#555; line-height: 1.5;">
                                            Your interest will be calculated based on the terms of your agreement. You can track your profit in your personal account.
                                        </p>

                                        <p style="margin-top:40px; color: #333;">
                                            Sincerely,<br>
                                            <strong style="font-size: 16px;">MMMBank Team</strong>
                                        </p>
                                    </div>

                                    <div style="background:#f9f9f9; padding:20px; text-align:center; font-size:12px; color:#999; border-top: 1px solid #eee;">
                                        © 2026 MMMBank. All rights reserved.<br>
                                        This is an automated message, please do not reply.
                                    </div>

                                </div>
                            </div>
                            """
            )

            Deposit.objects.create(user=request.user, account=account , amount=amount, duration=duration, rate=rate)




        return JsonResponse({"message": "Deposit opened successfully!"})

    except Account.DoesNotExist:
        return JsonResponse({"message": "Account not found."}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_close_piggy(request, piggy_id):
    try:
        data = json.loads(request.body)
        piggy = PiggyBank.objects.get(id=piggy_id, user=request.user)
        account_currency = data.get("currency")

        account = Account.objects.get(user=request.user, currency_type__code=account_currency)

        with transaction.atomic():
            remaining_balance = piggy.balance

            if remaining_balance > 0:
                cat_return, _ = Category.objects.get_or_create(name="Piggy Bank Closure", type=Category.DEPOSIT)
                Transaction.objects.create(
                    account=account,
                    amount=remaining_balance,
                    category=cat_return,
                    transaction_type=Category.DEPOSIT,
                    title=f"Returned funds from closed piggy: {piggy.name}"
                )

            piggy.delete()

        return JsonResponse({"message": f"Piggy bank closed. {remaining_balance} returned to your {account_currency} account."})

    except PiggyBank.DoesNotExist:
        return JsonResponse({"message": "Piggy Bank not found."}, status=404)
    except Account.DoesNotExist:
        return JsonResponse({"message": "Please select a valid account to return funds."}, status=400)
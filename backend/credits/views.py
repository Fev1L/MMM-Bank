import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.mail import send_mail
from credits.models import Credit, Account , Category, Transaction

from main.views import get_real_rates
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

MAX_LOAN_LIMIT = Decimal('200000.00')
DEFAULT_LOAN_INTEREST = 4.0

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_credits(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        active_credits = Credit.objects.filter(user=request.user).order_by('-created_at')
        credits_data = [{
            'id': c.id,
            'title': c.title,
            'amount': str(c.amount),
            'rate': c.interest_rate,
            'currency': c.account.currency_type.code if c.account else 'USD',
            'created_at': c.created_at.isoformat(),
            'is_active': c.is_active,
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

            send_mail(
                "Loan Approval Confirmation",
                f"Your loan for {amount} has been approved.",
                "no-reply@mmmbank.com",
                [request.user.email],
                html_message=f"""
                <div style="font-family: Arial, sans-serif; background-color:#f4f6f8; padding:20px;">
                    <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; overflow:hidden; box-shadow:0 6px 16px rgba(0,0,0,0.1);">

                        <!-- HEADER -->
                        <div style="background:linear-gradient(135deg, #6a0dad, #8e44ad); color:white; padding:25px; text-align:center;">
                            <h2 style="margin:0;">MMMBank</h2>
                            <p style="margin:5px 0 0;">Trusted Financial Services</p>
                        </div>

                        <!-- BODY -->
                        <div style="padding:30px;">
                            <h3 style="color:#333;">Loan Approved 🎉</h3>

                            <p style="color:#555;">
                                Dear {request.user.first_name or "Customer"},
                            </p>

                            <p style="color:#555;">
                                We are pleased to inform you that your loan application has been successfully approved.
                            </p>

                            <!-- DETAILS BOX -->
                            <div style="background:#f3e8ff; padding:15px; border-radius:10px; margin:20px 0; border-left:4px solid #6a0dad;">
                                <p><strong>💰 Approved Amount:</strong> {amount}</p>
                                <p><strong>Status:</strong> Approved</p>
                            </div>

                            <p style="color:#555;">
                                The funds will be credited to your account shortly in accordance with your agreement.
                            </p>

                            <p style="color:#555;">
                                If you have any questions, feel free to contact our support team.
                            </p>

                            <p style="margin-top:30px;">
                                Sincerely,<br>
                                <strong>MMMBank Team</strong>
                            </p>
                        </div>

                        <!-- FOOTER -->
                        <div style="background:#f1f1f1; padding:15px; text-align:center; font-size:12px; color:#777;">
                            © 2026 MMMBank. All rights reserved.<br>
                            This is an automated message, please do not reply.
                        </div>

                    </div>
                </div>
                """
            )
            return JsonResponse({'message': f'The loan for {amount} has been approved!'})

        except Account.DoesNotExist:
            return JsonResponse({'message': 'Account not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def repay_credit(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        credit_currency = data.get('credit_currency')
        pay_from_currency = data.get('account_currency')
        amount = Decimal(data.get('amount', 0))
        credit_id = data.get('id')

        if amount <= 0:
            return JsonResponse({'message': 'Amount must be greater than zero.'}, status=400)

        try:
            paying_account = Account.objects.get(user=request.user, currency_type__code=pay_from_currency)

            credit = Credit.objects.get(user=request.user, id=credit_id, is_active=True)

            if paying_account.balance < amount:
                return JsonResponse({'message': 'Not enough funds on balance.'}, status=400)

            pay_amount = amount

            if credit_currency != pay_from_currency:
                rates = get_real_rates()

                if credit_currency not in rates or pay_from_currency not in rates:
                    return JsonResponse({'status': 'error', 'message': 'A currency conversion error has occurred on the server. Please try again later.'}, status=500)

                rate_sender = Decimal(str(rates[pay_from_currency]))
                rate_receiver = Decimal(str(rates[credit_currency]))

                pay_amount = (amount / rate_sender) * rate_receiver
                pay_amount = pay_amount.quantize(Decimal('0.01'))

            credit_cat, _ = Category.objects.get_or_create(name="Loan payment", type=Category.WITHDRAW)

            with transaction.atomic():
                Transaction.objects.create(
                    account=paying_account,
                    amount=amount,
                    category=credit_cat,
                    transaction_type=Category.WITHDRAW,
                    title=f"Repayment of {credit.title} ({credit_currency})"
                )

                credit.amount -= pay_amount

                if credit.amount <= 0:
                    credit.amount = 0
                    credit.is_active = False
                    message = "Credit fully repaid and closed!"

                    credit.save()

                    send_mail(
                        "Credit Closed Confirmation",
                        f"Your credit '{credit.title}' has been fully repaid.",
                        "no-reply@mmmbank.com",
                        [request.user.email],
                        html_message=f"""
                        <div style="font-family: Arial, sans-serif; background-color:#f4f6f8; padding:20px;">
                            <div style="max-width:600px; margin:0 auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1);">

                                <!-- HEADER -->
            <div style="background:linear-gradient(135deg, #6a0dad, #8e44ad); color:white; padding:25px; text-align:center;">
                <h2 style="margin:0;">MMMBank</h2>
                <p style="margin:5px 0 0;">Trusted Financial Services</p>
            </div>

                                <!-- BODY -->
                                <div style="padding:30px;">
                                    <h3 style="color:#333;">Credit Closed Successfully</h3>

                                    <p style="color:#555;">
                                        Dear {request.user.first_name or "Customer"},
                                    </p>

                                    <p style="color:#555;">
                                        We would like to inform you that your credit account has been fully repaid and is now officially closed.
                                    </p>

                                    <!-- DETAILS BOX -->
                                    <div style="background:#f8f9fa; padding:15px; border-radius:8px; margin:20px 0;">
                                        <p><strong>Credit Name:</strong> {credit.title}</p>
                                        <p><strong>Status:</strong> Closed</p>
                                        <p><strong>Closure Date:</strong> {credit.updated_at if hasattr(credit, 'updated_at') else ''}</p>
                                    </div>

                                    <p style="color:#555;">
                                        Thank you for your trust and for using MMMBank services.  
                                        We look forward to serving you again.
                                    </p>

                                    <p style="color:#555;">
                                        If you have any questions, feel free to contact our support team.
                                    </p>

                                    <p style="margin-top:30px;">
                                        Sincerely,<br>
                                        <strong>MMMBank Team</strong>
                                    </p>
                                </div>

                                <!-- FOOTER -->
                                <div style="background:#f1f1f1; padding:15px; text-align:center; font-size:12px; color:#777;">
                                    © 2026 MMMBank. All rights reserved.<br>
                                    This is an automated message, please do not reply.
                                </div>

                            </div>
                        </div>
                        """
                    )

                    return JsonResponse({'message': message})


        except Account.DoesNotExist:
            return JsonResponse({'message': f"Account {pay_from_currency} not found."}, status=404)
        except Credit.DoesNotExist:
            return JsonResponse({'message': f"Active credit in {credit_currency} not found."}, status=404)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
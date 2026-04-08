from decimal import Decimal

import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import json
import random

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailVerification, Account, Currency, Transaction, Category, PaymentRequest
from django.conf import settings


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'status': 'ok',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'You are logged in!'
            }, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect username or password'}, status=401)

    return JsonResponse({'status': 'error', 'message': 'Only POST'}, status=405)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            if User.objects.filter(username=data.get('username')).exists():
                return JsonResponse({'status': 'error', 'message': 'This username is already taken'}, status=400)

            user = User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('firstName', ''),
                last_name=data.get('lastName', '')
            )

            profile = user.profile
            profile.nationality = data.get('nationality', '')
            profile.address_city = data.get('city', '')
            profile.address_street = data.get('street', '')
            profile.address_building = data.get('building', '')
            profile.save()

            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'status': 'ok',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'The user has been successfully created!'
            }, status=201)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'POST requests only'}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_logout():
    return JsonResponse({'status': 'success', 'message': 'Logged out'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_verification_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = str(random.randint(100000, 999999))

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'A user with this email address is already registered!'
            }, status=400)

        EmailVerification.objects.update_or_create(
            email=email, defaults={'code': code, 'created_at': timezone.now()}
        )

        send_mail(
            'Your MMM Bank verification code',
            f'Your code: {code}',
            'from@mmmbank.com',
            [email],
        )
        return JsonResponse({'status': 'ok', 'message': 'Code sent!'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')

        verify_obj = EmailVerification.objects.filter(email=email, code=code).last()

        if verify_obj and verify_obj.is_valid():
            verify_obj.delete()
            return JsonResponse({'status': 'ok', 'message': 'Email confirmed!'})
        return JsonResponse({'status': 'error', 'message': 'Incorrect or expired code'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_username(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()

            if not username or len(username) < 3:
                return JsonResponse({'available': False, 'message': 'Too short'}, status=200)

            exists = User.objects.filter(username=username).exists()
            return JsonResponse({
                'available': not exists,
                'message': 'Username is taken' if exists else 'Available'
            })
        except Exception:
            return JsonResponse({'error': 'Invalid data'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    profile = request.user.profile
    accounts = request.user.accounts.all()

    return JsonResponse({
        'personal': {
            'fullName': f"{request.user.first_name} {request.user.last_name}",
            'initials': f"{request.user.first_name[0]}{request.user.last_name[0]}" if request.user.first_name else "??",
            'nationality': profile.nationality,
            'avatar': profile.avatar.url if profile.avatar else None,
        },
        'settings': {
            'baseCurrency': profile.base_currency,
            'language': profile.language,
            'savingGoal': float(profile.saving_goal)
        },
        'accounts': [
            {'currency': acc.currency, 'balance': float(acc.balance)}
            for acc in accounts
        ]
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_data(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    user = request.user
    accounts = user.accounts.select_related('currency_type').all()
    all_currencies = Currency.objects.all()

    currencies_list = []
    for c in all_currencies:
        currencies_list.append({
            'code': c.code,
            'name': c.name,
            'symbol': c.symbol,
            'flag': c.flag
        })

    accounts_data = []

    for acc in accounts:
        accounts_data.append({
            'currency': acc.currency_type.name,
            'code': acc.currency_type.code,
            'balance': float(acc.balance),
            'symbol': acc.currency_type.symbol,
            'flag': acc.currency_type.flag,
            'iban': acc.iban,
        })

    return JsonResponse({
        'user': {
            'firstName': user.first_name,
            'lastName': user.last_name,
            'initials': f"{user.first_name[0]}{user.last_name[0]}" if user.first_name else "US",
        },
        'rates': get_real_rates(),
        'accounts': accounts_data,
        'availableCurrencies' : currencies_list
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            currency_code = data.get('currency')

            currency_obj = Currency.objects.get(code=currency_code)

            new_acc = Account.objects.create(
                user=request.user,
                currency_type=currency_obj,
                balance=0.00
            )

            return JsonResponse({
                'status': 'success',
                'account': {
                    'code': new_acc.currency_type.code,
                    'currency': new_acc.currency_type.name,
                    'symbol': new_acc.currency_type.symbol,
                    'flag': new_acc.currency_type.flag,
                    'balance': float(new_acc.balance)
                }
            })

        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'You already have an account in this currency'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=401)

    transactions = Transaction.objects.filter(account__user=request.user).select_related('category', 'account__currency_type').order_by('-created_at')

    data = []
    for tx in transactions:
        data.append({
            'id': tx.id,
            'title': tx.title,
            'amount': float(tx.amount),
            'type': tx.transaction_type,
            'date': tx.created_at.isoformat(),
            'currency_code': tx.account.currency_type.code,
            'category_name': tx.category.name if tx.category else "Uncategorised",
            'category_icon': tx.category.icon if tx.category else "fa-solid fa-money-bill-transfer"
        })

    return JsonResponse(data, safe=False)

def get_real_rates():
    rates = cache.get('exchange_rates')

    if not rates:
        try:
            api_key = "68f3333843fa6b81c7e5ac5e"
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
            response = requests.get(url)
            data = response.json()

            if data['result'] == 'success':
                rates = data['conversion_rates']
                cache.set('exchange_rates', rates, 43200)
        except Exception as e:
            rates = {"USD": 1.0, "UAH": 41.5, "EUR": 0.92}

    return rates

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_send_money(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(data.get('amount', 0))
        currency_code = data.get('currency')
        username_or_email = data.get('user')

        if amount <= 0:
            return JsonResponse({'status': 'error', 'message': 'The amount must be greater than zero'}, status=400)

        try:
            recipient = User.objects.get(username__iexact=username_or_email)
        except User.DoesNotExist:
            try:
                recipient = User.objects.get(email__iexact=username_or_email)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Users not found'}, status=404)

        if recipient == request.user:
            return JsonResponse({'status': 'error', 'message': 'You cannot send money to yourself'}, status=400)

        try:
            sender_account = Account.objects.get(user=request.user, currency_type__code=currency_code)
        except Account.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'You do not have an account with {currency_code}'}, status=400)

        if sender_account.balance < amount:
            return JsonResponse({'status': 'error', 'message': 'Not enough funds'}, status=400)

        recipient_account = Account.objects.filter(user=recipient, currency_type__code=currency_code).first()

        deposit_amount = amount
        recipient_currency_code = currency_code

        if not recipient_account:
            recipient_account = Account.objects.filter(user=recipient).order_by('id').first()

            if not recipient_account:
                return JsonResponse({'status': 'error', 'message': 'The user does not have any open accounts'}, status=400)

            recipient_currency_code = recipient_account.currency_type.code

            if recipient_currency_code != currency_code:
                rates = get_real_rates()

                if currency_code not in rates or recipient_currency_code not in rates:
                    return JsonResponse({'status': 'error', 'message': 'A currency conversion error has occurred on the server. Please try again later.'}, status=500)

                rate_sender = Decimal(str(rates[currency_code]))
                rate_receiver = Decimal(str(rates[recipient_currency_code]))

                deposit_amount = (amount / rate_sender) * rate_receiver
                deposit_amount = deposit_amount.quantize(Decimal('0.01'))

        transfer_cat, _ = Category.objects.get_or_create(name="Translation", type=Category.WITHDRAW)
        deposit_cat, _ = Category.objects.get_or_create(name="Receiving a money transfer", type=Category.DEPOSIT)

        with transaction.atomic():
            Transaction.objects.create(
                account=sender_account, amount=amount, category=transfer_cat, transaction_type=Category.WITHDRAW,
                title=f"Transfer to {recipient.username}"
            )
            Transaction.objects.create(
                account=recipient_account, amount=deposit_amount, category=deposit_cat, transaction_type=Category.DEPOSIT,
                title=f"Transfer from {request.user.username} (Original: {amount} {currency_code})"
            )

        if recipient.email:
            msg = f'Dear, {recipient.username}!\n\nUser {request.user.username} sent to you {amount} {currency_code}.'

            if recipient_currency_code != currency_code:
                msg += f'\nThe funds have been automatically converted and credited to your account: +{deposit_amount} {recipient_currency_code}.'
            else:
                msg += f'\nThe funds have been successfully credited to your account.'

            send_mail(
                subject='You have received a money transfer! 💸',
                message=msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True,
            )

        return JsonResponse({'status': 'success', 'message': 'The transfer has been successfully completed'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_request_money(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(data.get('amount', 0))
        currency_code = data.get('currency')
        username_or_email = data.get('user')

        try:
            recipient = User.objects.get(username__iexact=username_or_email)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        if recipient == request.user:
            return JsonResponse({'status': 'error', 'message': 'You cannot request money from yourself'}, status=400)

        payment_request = PaymentRequest.objects.create(
            sender=request.user,
            receiver=recipient,
            amount=amount,
            currency_code=currency_code,
            type=PaymentRequest.REQUEST,
            message=f"{request.user.username} is asking you for {amount} {currency_code}"
        )

        if recipient.email:
            pay_link = f"http://localhost:4200/pay-request/{payment_request.id}"
            send_mail(
                subject='Money Request 📩',
                message=f'Hello!\n\n{request.user.username} requested {amount} {currency_code} from you.\n'
                        f'To pay, click here: {pay_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
            )

        return JsonResponse({'status': 'success', 'message': 'Request sent successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_confirm_payment_request(request, request_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    pay_req = get_object_or_404(PaymentRequest, id=request_id, receiver=request.user, type=PaymentRequest.REQUEST)

    if pay_req.is_completed:
        return JsonResponse({'status': 'error', 'message': 'This request has already been paid'}, status=400)

    try:
        sender_acc = Account.objects.get(user=request.user, currency_type__code=pay_req.currency_code)
    except Account.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'You dont have a {pay_req.currency_code} account to pay this'}, status=400)

    if sender_acc.balance < pay_req.amount:
        return JsonResponse({'status': 'error', 'message': 'Insufficient funds'}, status=400)

    receiver_acc = Account.objects.filter(user=pay_req.sender, currency_type__code=pay_req.currency_code).first()

    recipient = pay_req.sender
    recipient_account = Account.objects.filter(user=recipient, currency_type__code=pay_req.currency_code).first()

    deposit_amount = pay_req.amount

    if not recipient_account:
        recipient_account = Account.objects.filter(user=recipient).order_by('id').first()
        if not recipient_account:
            return JsonResponse({'status': 'error', 'message': 'Recipient has no accounts'}, status=400)

        final_currency = recipient_account.currency_type.code
        rates = get_real_rates()

        rate_from = Decimal(str(rates[pay_req.currency_code]))
        rate_to = Decimal(str(rates[final_currency]))

        deposit_amount = (pay_req.amount / rate_from) * rate_to
        deposit_amount = deposit_amount.quantize(Decimal('0.01'))

    with transaction.atomic():
        Transaction.objects.create(
            account=sender_acc, amount=pay_req.amount, transaction_type=Category.WITHDRAW,
            title=f"Payment for request from {pay_req.sender.username}"
        )
        Transaction.objects.create(
            account=receiver_acc, amount=deposit_amount, transaction_type=Category.DEPOSIT,
            title=f"Money received from request to {request.user.username}"
        )

        pay_req.is_completed = True
        pay_req.save()

    return JsonResponse({'status': 'success', 'message': 'Payment successful!'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_send_gift(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(data.get('amount', 0))
        currency_code = data.get('currency')
        username_or_email = data.get('user')
        message = data.get('message', 'A gift for you! 🎁')

        try:
            recipient = User.objects.get(username__iexact=username_or_email)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        try:
            sender_account = Account.objects.get(user=request.user, currency_type__code=currency_code)
        except Account.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'You do not have an account with {currency_code}'}, status=400)

        if sender_account.balance < amount:
            return JsonResponse({'status': 'error', 'message': 'Not enough funds'}, status=400)

        gift_cat, _ = Category.objects.get_or_create(name="Gift", type=Category.WITHDRAW)

        with transaction.atomic():
            Transaction.objects.create(
                account=sender_account, amount=amount, category=gift_cat, transaction_type=Category.WITHDRAW,
                title=f"Sending a gift {recipient.username}"
            )

            gift_req = PaymentRequest.objects.create(
                sender=request.user, receiver=recipient, amount=amount,
                currency_code=currency_code, type=PaymentRequest.GIFT, message=message
            )

        if recipient.email:
            claim_link = f"http://localhost:4200/claim-gift/{gift_req.id}"
            send_mail(
                subject='You have received a cash gift! 🎁',
                message=f'Hello!\n\n{request.user.username} sent you {amount} {currency_code}.\nMessage: {message}\n\nClick the link to collect your money:\n{claim_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
            )

        return JsonResponse({'status': 'success', 'message': 'The gift has been successfully sent'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_claim_gift(request, request_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    gift_req = get_object_or_404(PaymentRequest, id=request_id, receiver=request.user, type=PaymentRequest.GIFT)

    if gift_req.is_completed:
        return JsonResponse({'status': 'error', 'message': 'This gift has already been received'}, status=400)

    recipient_account, _ = Account.objects.get_or_create(
        user=request.user,
        currency_type_id=gift_req.currency_code,
        defaults={'balance': 0}
    )

    deposit_cat, _ = Category.objects.get_or_create(name="Receiving a gift", type=Category.DEPOSIT)

    with transaction.atomic():
        Transaction.objects.create(
            account=recipient_account, amount=gift_req.amount, category=deposit_cat, transaction_type=Category.DEPOSIT,
            title=f"Gift from {gift_req.sender.username}"
        )
        gift_req.is_completed = True
        gift_req.save()

    return JsonResponse({'status': 'success', 'message': f'A gift of {gift_req.amount} {gift_req.currency_code} credited!'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_exchange_money(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(data.get('amount', 0))
        from_currency = data.get('from_currency')
        to_currency = data.get('to_currency')

        if amount <= 0:
            return JsonResponse({'status': 'error', 'message': 'The sum must be greater than zero'}, status=400)

        if from_currency == to_currency:
            return JsonResponse({'status': 'error', 'message': 'Select different accounts for the exchange'}, status=400)

        try:
            from_account = Account.objects.get(user=request.user, currency_type__code=from_currency)
            to_account = Account.objects.get(user=request.user, currency_type__code=to_currency)
        except Account.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Account not found'}, status=404)

        if from_account.balance < amount:
            return JsonResponse({'status': 'error', 'message': 'Insufficient funds in the account'}, status=400)

        rates = get_real_rates()
        if from_currency not in rates or to_currency not in rates:
            return JsonResponse({'status': 'error', 'message': 'Error retrieving exchange rates'}, status=500)

        rate_from = Decimal(str(rates[from_currency]))
        rate_to = Decimal(str(rates[to_currency]))

        converted_amount = (amount / rate_from) * rate_to
        converted_amount = converted_amount.quantize(Decimal('0.01'))

        exchange_out_cat, _ = Category.objects.get_or_create(name="Currency Exchange (Out)", type=Category.WITHDRAW)
        exchange_in_cat, _ = Category.objects.get_or_create(name="Currency Exchange (In)", type=Category.DEPOSIT)

        with transaction.atomic():
            Transaction.objects.create(
                account=from_account, amount=amount, category=exchange_out_cat, transaction_type=Category.WITHDRAW,
                title=f"Exchange to {to_currency}"
            )
            Transaction.objects.create(
                account=to_account, amount=converted_amount, category=exchange_in_cat, transaction_type=Category.DEPOSIT,
                title=f"Exchange from {from_currency} (Rate: {rate_from}/{rate_to})"
            )

        amount = amount.quantize(Decimal('0.01'))

        return JsonResponse({
            'status': 'success',
            'message': f'{amount} {from_currency} has been successfully exchanged for {converted_amount} {to_currency}'
        })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_account(request, currency_code):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    if request.method == 'DELETE':
        try:
            account = Account.objects.get(user=request.user, currency_type__code=currency_code)

            if account.balance > 0:
                return JsonResponse({'status': 'error', 'message': 'It is not possible to close an account with a positive balance. Please transfer the funds.'}, status=400)

            account.delete()
            return JsonResponse({'status': 'success', 'message': 'The account has been successfully closed'})

        except Account.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Account not found'}, status=404)
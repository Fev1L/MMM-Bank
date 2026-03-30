import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import json
import random

from .models import EmailVerification, Account, Currency, Transaction


@never_cache
@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'ok', 'message': 'You are logged in!'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect username or password'}, status=401)

    return JsonResponse({'status': 'error', 'message': 'Only POST'}, status=405)

@csrf_exempt
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

            login(request, user)

            return JsonResponse({
                'status': 'ok',
                'message': 'The user has been successfully created!'
            }, status=201)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'POST requests only'}, status=405)

@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({'status': 'success', 'message': 'Logged out'})

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
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
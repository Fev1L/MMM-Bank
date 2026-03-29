from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import json
import random

from .models import EmailVerification , Account

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

    accounts_data = []
    total_balance_uah = 0

    for acc in accounts:
        accounts_data.append({
            'currency': acc.currency_type.name,
            'code': acc.currency_type.code,
            'balance': float(acc.balance),
            'symbol': acc.currency_type.symbol,
            'flag': acc.currency_type.flag,
        })
        total_balance_uah += float(acc.balance)

    return JsonResponse({
        'user': {
            'firstName': user.first_name,
            'lastName': user.last_name,
            'initials': f"{user.first_name[0]}{user.last_name[0]}" if user.first_name else "US",
        },
        'totalBalance': total_balance_uah,
        'accounts': accounts_data,
    })

@csrf_exempt
def create_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            currency_code = data.get('currency')

            new_acc = Account.objects.create(
                user=request.user,
                currency=currency_code,
                balance=0.00
            )

            return JsonResponse({
                'status': 'success',
                'account': {
                    'currency': new_acc.currency,
                    'balance': float(new_acc.balance)
                }
            })

        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'You already have an account in this currency'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
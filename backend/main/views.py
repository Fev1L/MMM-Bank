from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import random

from main.models import EmailVerification

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
                first_name=data.get('name', ''),
                last_name=data.get('surname', '')
            )

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
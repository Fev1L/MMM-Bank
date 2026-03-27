from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'ok', 'message': 'Ви увійшли!'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Невірний логін або пароль'}, status=401)

    return JsonResponse({'status': 'error', 'message': 'Тільки POST'}, status=405)
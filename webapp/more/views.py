from django.shortcuts import render

from .models import Casino_Transaction

def index(request):
    return render(request, 'more/index.html')

def casino_home(request):
    account = request.user.account
    balance = account.balance
    transactions = Casino_Transaction.objects.filter(account=account).order_by('-created_at')[:3]
    temp = {
        'balance': balance,
        'transactions': transactions
        }
    return render(request, 'more/casino/casino.html', temp)

def casino_slots(request):
    account = request.user.account
    balance = account.balance
    temp = {
        'balance': balance,
    }
    return render(request, 'more/casino/slots.html', temp)
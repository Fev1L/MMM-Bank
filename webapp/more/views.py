from django.shortcuts import render

def index(request):
    return render(request, 'more/index.html')

def casino_home(request):
    account = request.user.account
    balance = account.balance
    return render(request, 'more/casino/casino.html',
                  {'balance': balance}
                  )

def casino_slots(request):
    return render(request, 'more/casino/slots.html')
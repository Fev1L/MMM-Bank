from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Transaction

def index(request):
    if request.user.is_authenticated:
        account = request.user.account
        balance = account.balance
        transactions = Transaction.objects.all().order_by('-created_at')
        total_income = 0
        for transaction in transactions:
            if transaction.type == Transaction.DEPOSIT:
                total_income += transaction.amount
        total_expenses = 0
        for transaction in transactions:
            if transaction.type == Transaction.WITHDRAW:
                total_expenses += transaction.amount
        saving_goal = 0
        investments = 0
        imrt = {
            "balance" : balance,
            "transactions" : transactions,
            "card": account.card,
            "total_income" : total_income,
            "total_expenses" : total_expenses,
            "saving_goal" : saving_goal,
            "investments" : investments,
        }
        return render(request, 'main/index.html', imrt)
    else:
        return render(request, 'main/index.html')

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
     
    if request.method == 'POST':
         user = authenticate(username=request.POST['username'], password=request.POST['password'])
         if user is not None:
             login(request, user)
             if request.session.get('next'):
                return redirect(request.session.pop('next'))
             
             return redirect('home')
         else:
             messages.error(request, 'Invalid credentials')
             return redirect('login_user')
         
    if request.GET.get('next'):
        request.session['next'] = request.GET['next']

    return render(request, 'main/users/login.html')

def register(request):
    if request.user.is_authenticated:
         return redirect('home')
    
    if request.method == 'POST':
        user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
        login(request, user)
        return redirect('home')
    
    return render(request, 'main/users/register.html')

def logout_user(request):
    logout(request)
     
    return redirect('home')
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import transaction as db_transaction
from .models import Transaction, Contact, Category
from .forms import AddContactForm
from decimal import Decimal

def index(request):
    if request.user.is_authenticated:
        account = request.user.account
        balance = account.balance
        contacts = Contact.objects.filter(owner=request.user)[:4]
        transactions = Transaction.objects.filter(account=account).order_by('-created_at')[:4]
        total_income = 0
        for transaction in transactions:
            if transaction.category.type == Transaction.DEPOSIT:
                total_income += transaction.amount
        total_expenses = 0
        for transaction in transactions:
            if transaction.category.type == Transaction.WITHDRAW:
                total_expenses += transaction.amount
        saving_goal = 0
        investments = 0
        imrt = {
            "balance" : balance,
            "transactions" : transactions,
            "total_income" : total_income,
            "total_expenses" : total_expenses,
            "saving_goal" : saving_goal,
            "investments" : investments,
            "contacts" : contacts
        }
        return render(request, 'main/index.html', imrt)
    else:
        return render(request, 'main/index.html')


def history(request):
    account = request.user.account
    balance = account.balance
    contacts = Contact.objects.filter(owner=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-created_at')
    return render(request, 'main/history.html',{'contacts': contacts, "balance" : balance, "transactions" : transactions,})

def profile(request):
    return render(request, 'main/profile.html')

@login_required
def contacts_list(request):
    account = request.user.account
    balance = account.balance
    contacts = Contact.objects.filter(owner=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-created_at')[:4]
    return render(request, 'main/contacts/transfer.html', {'contacts': contacts, "balance" : balance, "transactions" : transactions,})

@login_required
def add_contact(request):
    if request.method == 'POST':
        form = AddContactForm(request.POST)
        if form.is_valid():
            friend = form.cleaned_data['username_or_email']
            if friend == request.user:
                form.add_error('username_or_email', "You can't add yourself.")
            else:
                Contact.objects.get_or_create(owner=request.user, friend=friend)
                return redirect('contacts_list')
    else:
        form = AddContactForm()
    return render(request, 'main/contacts/add_contact.html', {'form': form})

@login_required
def send_money(request, friend_id):
    recipient = User.objects.get(pk=friend_id)
    sender_account = request.user.account
    recipient_account = recipient.account

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if sender_account.balance < amount:
            return render(request, 'main/contacts/send_money.html', {'error': "Not enough balance", 'friend': recipient})

        transfer_category, _ = Category.objects.get_or_create(name="Transfer", type=Category.WITHDRAW)

        with db_transaction.atomic():
            Transaction.objects.create(
                account=sender_account,
                amount=amount,
                category=transfer_category,
                title=f"Transfer to {recipient.username}"
            )
            deposit_category, _ = Category.objects.get_or_create(name="Deposit", type=Category.DEPOSIT)
            Transaction.objects.create(
                account=recipient_account,
                amount=amount,
                category=deposit_category,
                title=f"Transfer from {request.user.username}"
            )
        return redirect('contacts_list')

    return render(request, 'main/contacts/send_money.html', {'friend': recipient})

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
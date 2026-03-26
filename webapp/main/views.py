from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import transaction as db_transaction
from .models import Transaction, Contact, Category, InboxMessage
from .forms import AddContactForm
from decimal import Decimal, InvalidOperation
from .services import make_transfer
from deposits.models import Purchase

def index(request):
    if request.user.is_authenticated:
        account = request.user.account
        balance = account.balance
        contacts = Contact.objects.filter(owner=request.user)[:4]
        transactions = Transaction.objects.filter(account=account).order_by('-created_at')[:4]
        transactionsStats = Transaction.objects.filter(account=account).order_by('-created_at')
        total_income = 0
        for transaction in transactionsStats:
            if transaction.category.type == Transaction.DEPOSIT:
                total_income += transaction.amount
        total_expenses = 0
        for transaction in transactionsStats:
            if transaction.category.type == Transaction.WITHDRAW:
                total_expenses += transaction.amount
        saving_goal = account.saving_goal
        investments = 0
        purchases = Purchase.objects.filter(user=request.user)
        for p in purchases:
            investments += p.total_price

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


@login_required
def history(request):
    account = request.user.account
    balance = account.balance
    contacts = Contact.objects.filter(owner=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-created_at')
    return render(request, 'main/history.html',{'contacts': contacts, "balance" : balance, "transactions" : transactions,})

@login_required
def profile(request):
    return render(request, 'main/profile.html')

@login_required
def goals(request):
    account = request.user.account

    if request.method == 'POST':
        saving_goal = request.POST.get('saving_goal')

        try:
            account.saving_goal = Decimal(saving_goal)
            account.save()
        except InvalidOperation:
            return render(request, 'main/layout/goals.html', {
                'error': 'Invalid number',
                'saving_goal': account.saving_goal
            })

        if saving_goal:
            account.saving_goal = Decimal(saving_goal)
            account.save()

            return redirect('home')

    return render(request, 'main/layout/goals.html', {
        'saving_goal': account.saving_goal
    })

@login_required
def inbox(request):
    messages = InboxMessage.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'main/mail/inbox.html', {'messages': messages})

@login_required
def message_detail(request, message_id):
    msg = get_object_or_404(InboxMessage, id=message_id, receiver=request.user)

    if not msg.is_read:
        msg.is_read = True
        msg.save()

    return render(request, 'main/mail/mail.html', {'msg': msg})

@login_required
def contacts_list(request):
    account = request.user.account
    balance = account.balance
    contacts = Contact.objects.filter(owner=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-created_at')[:4]
    return render(request, 'main/transfer.html', {'contacts': contacts, "balance" : balance, "transactions" : transactions,})

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
                return redirect('home')
    else:
        form = AddContactForm()
    return render(request, 'main/contacts/add_contact.html', {'form': form})

@login_required
def send_money(request, friend_id=None):
    recipient = None

    if friend_id:
        recipient = get_object_or_404(User, pk=friend_id)

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if not recipient:
            username_or_email = request.POST.get('user')

            try:
                recipient = User.objects.get(username__iexact=username_or_email)
            except User.DoesNotExist:
                try:
                    recipient = User.objects.get(email__iexact=username_or_email)
                except User.DoesNotExist:
                    return render(request, 'main/contacts/send_money.html', {
                        'error': "User not found"
                    })

        try:
            make_transfer(request.user, recipient, amount)
            return redirect('home')
        except ValidationError as e:
            return render(request, 'main/contacts/send_money.html', {
                'error': str(e),
                'friend': recipient
            })

    return render(request, 'main/contacts/send_money.html', {
        'friend': recipient
    })

@login_required
def request_money(request, friend_id=None):
    recipient = None

    if friend_id:
        recipient = get_object_or_404(User, pk=friend_id)

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if not recipient:
            username_or_email = request.POST.get('user')

            try:
                recipient = User.objects.get(username__iexact=username_or_email)
            except User.DoesNotExist:
                try:
                    recipient = User.objects.get(email__iexact=username_or_email)
                except User.DoesNotExist:
                    return render(request, 'main/contacts/request_money.html', {
                        'error': "User not found"
                    })

        if recipient == request.user:
            return render(request, 'main/contacts/request_money.html', {
                'error': "You cannot request from yourself"
            })

        InboxMessage.objects.create(
            receiver=recipient,
            sender=request.user,
            title="Payment Request 💸",
            content=f"{request.user.username} requests {amount}",
            type=InboxMessage.REQUEST,
            amount=amount
        )

        return redirect('home')

    return render(request, 'main/contacts/request_money.html', {
        'friend': recipient
    })

@login_required
def send_gift(request):

    if request.method == 'POST':
        username_or_email = request.POST.get('user')
        amount = Decimal(request.POST.get('amount'))
        message = request.POST.get('message')

        if not message:
            message = f"{request.user.username} sent you a gift of ${amount}"

        try:
            recipient = User.objects.get(username__iexact=username_or_email)
        except User.DoesNotExist:
            try:
                recipient = User.objects.get(email__iexact=username_or_email)
            except User.DoesNotExist:
                return render(request, 'main/contacts/send_gift.html', {
                    'error': "User not found"
                })

        if recipient == request.user:
            return render(request, 'main/contacts/send_gift.html', {
                'error': "You cannot send gift to yourself"
            })

        sender_account = request.user.account

        if sender_account.balance < amount:
            return render(request, 'main/contacts/send_gift.html', {
                'error': "Not enough balance"
            })

        transfer_category, _ = Category.objects.get_or_create(
            name="Gift",
            type=Category.WITHDRAW
        )

        with db_transaction.atomic():
            Transaction.objects.create(
                account=sender_account,
                amount=amount,
                category=transfer_category,
                title=f"Gift to {recipient.username}"
            )

            InboxMessage.objects.create(
                receiver=recipient,
                sender=request.user,
                title="You received a gift 🎁",
                content=message,
                type=InboxMessage.GIFT,
                amount=amount
            )

        return redirect('home')

    return render(request, 'main/contacts/send_gift.html')

@login_required
def pay_request(request, message_id):
    msg = get_object_or_404(InboxMessage, id=message_id, receiver=request.user)

    if msg.is_paid:
        return redirect('inbox')

    sender_account = request.user.account
    recipient_account = msg.sender.account
    amount = msg.amount

    if sender_account.balance < amount:
        return render(request, 'main/mail/mail.html', {
            'msg': msg,
            'error': "Not enough balance"
        })

    transfer_category, _ = Category.objects.get_or_create(
        name="Transfer",
        type=Category.WITHDRAW
    )

    deposit_category, _ = Category.objects.get_or_create(
        name="Deposit",
        type=Category.DEPOSIT
    )

    with db_transaction.atomic():
        Transaction.objects.create(
            account=sender_account,
            amount=amount,
            category=transfer_category,
            title=f"Payment for request from {msg.sender.username}"
        )

        Transaction.objects.create(
            account=recipient_account,
            amount=amount,
            category=deposit_category,
            title=f"Payment received from {request.user.username}"
        )

        msg.is_paid = True
        msg.save()

    return redirect('inbox')


@login_required
def claim_gift(request, message_id):
    if request.method != 'POST':
        return redirect('inbox')

    msg = get_object_or_404(InboxMessage, id=message_id, receiver=request.user)

    if msg.is_paid:
        return redirect('inbox')

    recipient_account = request.user.account
    amount = msg.amount

    deposit_category, _ = Category.objects.get_or_create(
        name="Gift",
        type=Category.DEPOSIT
    )

    with db_transaction.atomic():
        Transaction.objects.create(
            account=recipient_account,
            amount=amount,
            category=deposit_category,
            title=f"Gift from {msg.sender.username}"
        )

        msg.is_paid = True
        msg.save()

    return redirect('inbox')

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
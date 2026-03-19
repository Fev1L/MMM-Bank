from decimal import Decimal

from django.shortcuts import render, redirect
from .models import PiggyBank, piggy_transactions, Deposit , Stock, Purchase
from main.models import Transaction, Category

def piggy_bank(request):

    piggy, created = PiggyBank.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        amount_raw = request.POST.get("amount")
        goal_raw = request.POST.get("goal")

        if goal_raw:
            try:
                piggy.goal = float(goal_raw)
            except ValueError:
                pass

        if amount_raw:
            try:
                amount = float(amount_raw)

                if action == "add" and amount > 0:
                    piggy.balance += amount
                    piggy_transactions.objects.create(
                        user=request.user,
                        amount=amount
                    )

                elif action == "withdraw" and amount > 0:
                    if piggy.balance >= amount:
                        piggy.balance -= amount

                        piggy_transactions.objects.create(
                            user=request.user,
                            amount=-amount
                        )
            except ValueError:
                pass

        piggy.save()

        return redirect('piggy_bank')


    percent = 0
    if piggy.goal > 0:
        percent = (piggy.balance / piggy.goal) * 100
        percent = min(int(percent), 100)


    transactions = piggy_transactions.objects.filter(user=request.user).order_by('-timestamp')[:10]

    return render(request, "deposits/piggy_bank.html", {
        "piggy": piggy,
        "percent": percent,
        "transactions": transactions,
    })


def open_deposit(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        duration = request.POST.get("duration")

        if amount and duration:
            amount = float(amount)
            duration = int(duration)


            rates = {
                3: 3,
                6: 5,
                12: 7,
                24: 9
            }

            rate = rates.get(duration, 5)
            transfer_category, _ = Category.objects.get_or_create(name="Open Deposit", type=Category.WITHDRAW)

            Transaction.objects.create(
                account=request.user.account,
                amount=Decimal(amount),
                category=transfer_category,
                title=f"Deposit open successfully"
            )

            Deposit.objects.create(
                user=request.user,
                amount=amount,
                duration=duration,
                rate=rate
            )

        return redirect('index')

    return render(request, "deposits/open_deposit.html")


def index(request):
    account = request.user.account
    balance = account.balance
    deposits = Deposit.objects.filter(user=request.user, is_active=True)
    history = Deposit.objects.filter(user=request.user, is_active=False)

    chart_data = []
    total = 0

    for d in deposits:
        total += d.amount + (d.amount * d.rate / 100)
        chart_data.append(total)

    return render(request, 'deposits/index.html', {
        "deposits": deposits,
        "history": history,
        "chart_data": chart_data,
        "balance": balance,
    })


def buy_bonds(request):
    stocks = Stock.objects.all()
    purchases = Purchase.objects.filter(user=request.user).order_by("-created_at")[:10]

    if request.method == "POST":
        stock_id = request.POST.get("stock")
        quantity = request.POST.get("quantity")

        if stock_id and quantity:
            try:
                stock = Stock.objects.get(id=stock_id)
                quantity = int(quantity)

                total_price = stock.price * quantity

                Purchase.objects.create(
                    user=request.user,
                    stock=stock,
                    quantity=quantity,
                    total_price=total_price
                )

            except:
                pass

        return redirect("buy_bonds")

    return render(request, "deposits/bonds.html", {
        "stocks": stocks,
        "purchases": purchases
    })
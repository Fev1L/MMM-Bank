from django.shortcuts import render, redirect
from .models import PiggyBank, Transaction


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
                    Transaction.objects.create(
                        user=request.user,
                        amount=amount
                    )

                elif action == "withdraw" and amount > 0:
                    if piggy.balance >= amount:
                        piggy.balance -= amount

                        Transaction.objects.create(
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


    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')[:10]

    return render(request, "deposits/piggy_bank.html", {
        "piggy": piggy,
        "percent": percent,
        "transactions": transactions,
    })


def open_deposit(request):
    return render(request, "deposits/open_deposit.html")


def index(request):
    return render(request, 'deposits/index.html')


def buy_bonds(request):
    return render(request, "deposits/bonds.html")
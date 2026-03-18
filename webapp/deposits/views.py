from django.shortcuts import render, redirect
from .models import PiggyBank, piggy_transactions
from .models import Deposit

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

            Deposit.objects.create(
                user=request.user,
                amount=amount,
                duration=duration,
                rate=rate
            )

        return redirect('index')

    return render(request, "deposits/open_deposit.html")


def index(request):
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
        "chart_data": chart_data
    })


def buy_bonds(request):
    return render(request, "deposits/bonds.html")
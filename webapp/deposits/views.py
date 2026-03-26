from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import PiggyBank, PiggyTransaction, Deposit , Stock, Purchase
from main.models import Transaction, Category



def piggy_bank(request):
    if not request.user.is_authenticated:
        return redirect('login')  # або куди потрібно

    piggies = PiggyBank.objects.filter(user=request.user).order_by('-created_at')

    selected_piggy = None
    percent = 0
    transactions = []

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            name = request.POST.get("name", "").strip()
            if name:
                PiggyBank.objects.create(
                    user=request.user,
                    name=name,
                    balance=Decimal('0.00'),
                    goal=Decimal('0.00')
                )
            return redirect('piggy_bank')

        elif action in ["add", "withdraw"]:
            try:
                piggy_id = int(request.POST.get("piggy_id"))
                amount = Decimal(request.POST.get("amount", 0))

                piggy = PiggyBank.objects.get(id=piggy_id, user=request.user)

                if action == "add" and amount > 0:
                    piggy.balance += amount
                    PiggyTransaction.objects.create(   # ← змінено
                        user=request.user,
                        piggy=piggy,
                        amount=amount,
                        transaction_type='add'
                    )

                elif action == "withdraw" and amount > 0:
                    if piggy.balance >= amount:
                        piggy.balance -= amount
                        PiggyTransaction.objects.create(   # ← змінено
                            user=request.user,
                            piggy=piggy,
                            amount=amount,                 # залиш позитивне, тип покаже withdraw
                            transaction_type='withdraw'
                        )

                piggy.save()

            except Exception as e:
                # Краще логувати помилку в production, але для розробки можна pass
                pass

            return redirect('piggy_bank')

    # GET частина
    if piggies.exists():
        selected_piggy = piggies.first()

        if selected_piggy.goal > 0:
            percent = min(int((selected_piggy.balance / selected_piggy.goal) * 100), 100)

        # Головне виправлення тут:
        transactions = PiggyTransaction.objects.filter(   # ← змінено назву моделі
            piggy=selected_piggy
        ).order_by('-timestamp')[:10]

    return render(request, "deposits/piggy_bank.html", {
        "piggies": piggies,
        "selected_piggy": selected_piggy,
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

    user_balance = getattr(request.user.account, 'balance', Decimal('0'))

    MIN_INVESTMENT = Decimal('100.00')
    MAX_PERCENT_OF_BALANCE = Decimal('0.50')

    lower_bound = MIN_INVESTMENT
    upper_bound = (user_balance * MAX_PERCENT_OF_BALANCE).quantize(Decimal('0.01'))

    if request.method == "POST":
        stock_id = request.POST.get("stock")
        quantity_str = request.POST.get("quantity")

        if not stock_id or not quantity_str:
            messages.error(request, "Please select a stock and enter quantity.")
            return redirect("buy_bonds")

        try:
            stock = get_object_or_404(Stock, id=stock_id)
            quantity = int(quantity_str)

            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")

            total_price = round(stock.price * quantity, 2)

            if total_price < lower_bound:
                messages.error(request, f"Minimum investment amount is ${lower_bound}")
                return redirect("buy_bonds")

            if total_price > upper_bound:
                messages.error(request, f"Maximum investment amount is ${upper_bound}")
                return redirect("buy_bonds")

            if total_price > user_balance:
                messages.error(request, "Insufficient balance!")
                return redirect("buy_bonds")


            account = request.user.account
            account.balance -= total_price
            account.save()


            Purchase.objects.create(
                user=request.user,
                stock=stock,
                quantity=quantity,
                total_price=total_price,
            )

            messages.success(request, f"Successfully purchased {quantity} shares of {stock.name} for ${total_price}")

        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "An error occurred during purchase.")

        return redirect("buy_bonds")

    return render(request, "deposits/bonds.html", {
        "stocks": stocks,
        "purchases": purchases,
        "balance": round(user_balance, 2),
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
    })
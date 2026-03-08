from django.shortcuts import render

def open_deposit(request):
    return render(request, "deposits/open_deposit.html")

def index(request):
    return render(request, 'deposits/index.html')

def piggy_bank(request):
    return render(request, "deposits/piggy_bank.html")

def buy_bonds(request):
    return render(request, "deposits/bonds.html")
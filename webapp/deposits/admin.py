from django.contrib import admin

from .models import PiggyBank, PiggyTransaction, Stock, Deposit, Purchase

admin.site.register(PiggyBank)

admin.site.register(PiggyTransaction)

admin.site.register(Stock)

admin.site.register(Deposit)

admin.site.register(Purchase)

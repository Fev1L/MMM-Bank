from django.contrib import admin

from .models import PiggyBank, piggy_transactions, Stock, Deposit, Purchase

admin.site.register(PiggyBank)

admin.site.register(piggy_transactions)

admin.site.register(Stock)

admin.site.register(Deposit)

admin.site.register(Purchase)

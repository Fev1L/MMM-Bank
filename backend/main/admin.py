from django.contrib import admin

from .models import Account, UserProfile, Currency, Transaction, Category

admin.site.register(Account)

admin.site.register(UserProfile)

admin.site.register(Currency)

admin.site.register(Category)

admin.site.register(Transaction)
from django.contrib import admin

from .models import Account, Transaction, Category, Contact

admin.site.register(Account)

admin.site.register(Transaction)

admin.site.register(Category)

admin.site.register(Contact)
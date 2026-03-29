from django.contrib import admin

from .models import Account, UserProfile, Currency

admin.site.register(Account)

admin.site.register(UserProfile)

admin.site.register(Currency)
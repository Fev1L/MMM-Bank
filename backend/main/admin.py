from django.contrib import admin

from .models import Account, UserProfile

admin.site.register(Account)

admin.site.register(UserProfile)
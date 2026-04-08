from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

from main.models import Account

class PiggyBank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default="My Piggy Bank")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='piggy', null=True)
    goal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.balance} ({self.user.first_name} {self.user.last_name})"

class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='deposits', null=True)
    rate = models.FloatField()
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def profit(self):
        return self.amount * self.rate / 100
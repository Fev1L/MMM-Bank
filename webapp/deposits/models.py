from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class PiggyBank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default="My Piggy Bank")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    goal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name} - ${self.balance} ({self.user.username})"


class PiggyTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    piggy = models.ForeignKey(PiggyBank, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('add', 'Add'), ('withdraw', 'Withdraw')])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type} ${self.amount} - {self.piggy.name}"


# Нижче залишаємо без змін
class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    rate = models.FloatField()
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def profit(self):
        return self.amount * self.rate / 100


class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Purchase(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
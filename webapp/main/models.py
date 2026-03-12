from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import transaction
import random

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} account"

class Card(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    VISA = "visa"
    MASTERCARD = "mastercard"
    AMERICAN_EXPRESS = "american_express"
    CARD_TYPE = [
        (VISA, "Visa"),
        (MASTERCARD, "Mastercard"),
        (AMERICAN_EXPRESS, "American Express"),
    ]

    card_number = models.CharField(max_length=16)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    cvv = models.CharField(max_length=3)
    type = models.CharField(max_length=20, choices=CARD_TYPE)

    def __str__(self):
        return f"Card ****{self.card_number[-4:]}"

    @property
    def masked_number(self):
        return f"•••• {self.card_number[-4:]}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100 , default="fa-solid fa-circle-arrow-down")

    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSACTION_TYPES = [
        (DEPOSIT, "Deposit"),
        (WITHDRAW, "Withdraw"),
    ]

    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"{self.name}"
class Transaction(models.Model):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Transaction")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Transactions cannot be edited")
        if self.category.type == self.DEPOSIT:
            self.account.balance += self.amount
        elif self.category.type == self.WITHDRAW:
            if self.account.balance < self.amount:
                raise ValidationError("Not enough money")
            self.account.balance -= self.amount

        self.account.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.type} - {self.amount}"

@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
        Card.objects.create(
            account=Account,
            card_number=str(random.randint(1000000000000000, 9999999999999999)),
            expiry_month=12,
            expiry_year=2030,
            cvv=str(random.randint(100, 999)),
            type="visa"
        )
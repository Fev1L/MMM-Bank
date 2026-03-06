from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import transaction

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} account"

class Category(models.Model):
    name = models.CharField(max_length=100)

    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSACTION_TYPES = [
        (DEPOSIT, "Deposit"),
        (WITHDRAW, "Withdraw"),
    ]

    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    def __str__(self):
        return self.name
class Transaction(models.Model):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Transaction")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=Category.TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Transactions cannot be edited")
        if self.type == self.DEPOSIT:
            self.account.balance += self.amount
        elif self.type == self.WITHDRAW:
            if self.account.balance < self.amount:
                raise ValidationError("Not enough money")
            self.account.balance -= self.amount

        self.account.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type} - {self.amount}"

@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
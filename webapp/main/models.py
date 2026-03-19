from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import transaction

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saving_goal = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    def __str__(self):
        return f"{self.user.username} account"


class Contact(models.Model):
    owner = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('owner', 'friend')

    def __str__(self):
        return f"{self.owner.username} -> {self.friend.username}"

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

class InboxMessage(models.Model):
    SYSTEM = "system"
    USER = "user"
    REQUEST = "request"
    GIFT = "gift"

    MESSAGE_TYPE = [
        (SYSTEM, "System"),
        (USER, "User"),
        (REQUEST, "Request"),
        (GIFT, "Gift"),
    ]

    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=10, choices=MESSAGE_TYPE, default=SYSTEM)

    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} -> {self.receiver.username}"

@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)

        InboxMessage.objects.create(
            receiver=instance,
            title="Welcome 🎉",
            content="Welcome to our bank! Your account has been created."
        )
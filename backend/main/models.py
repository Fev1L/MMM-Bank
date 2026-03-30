from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class EmailVerification(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 600


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_street = models.CharField(max_length=100, blank=True)
    address_building = models.CharField(max_length=20, blank=True)

    base_currency = models.CharField(max_length=3, default='USD')
    language = models.CharField(max_length=5, default='en')

    saving_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Profile for {self.user.username}"

class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    flag = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code} ({self.name})"

class Account(models.Model):
    user = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)

    currency_type = models.ForeignKey(Currency, on_delete=models.PROTECT)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'currency_type'],
                name='unique_user_currency'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.currency_type} account"

@receiver(post_save, sender=User)
def create_user_bank_data(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class Category(models.Model):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSACTION_TYPES = [
        (DEPOSIT, "Top-up"),
        (WITHDRAW, "Consumption"),
    ]

    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, default="fa-solid fa-question")
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSACTION_TYPES = [
        (DEPOSIT, "Top-up"),
        (WITHDRAW, "Consumption"),
    ]

    account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='transactions')

    title = models.CharField(max_length=255, default="Transaction")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Transactions cannot be modified once they have been created!")

        if self.amount <= 0:
            raise ValidationError("The transaction amount must be greater than zero.")

        if not self.transaction_type and self.category:
            self.transaction_type = self.category.type

        if self.transaction_type == self.DEPOSIT:
            self.account.balance += self.amount

        elif self.transaction_type == self.WITHDRAW:
            if self.account.balance < self.amount:
                raise ValidationError("There are insufficient funds in your account!")
            self.account.balance -= self.amount

        self.account.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.upper()} | {self.amount} {self.account.currency_type.code} | {self.created_at.strftime('%Y-%m-%d')}"
from django.contrib.auth.models import User
from django.db import models
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

def get_default_currency():
    currency, created = Currency.objects.get_or_create(
        code='USD',
        defaults={'name': 'US Dollar', 'symbol': '$', 'flag': '🇺🇸'}
    )
    return currency.pk

class Account(models.Model):
    user = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)

    currency_type = models.ForeignKey(Currency, on_delete=models.PROTECT, default=get_default_currency)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.currency_type} account"

@receiver(post_save, sender=User)
def create_user_bank_data(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        Account.objects.create(user=instance, currency='USD', balance=0)
import uuid

from django.contrib.auth.models import User
from django.db import models

from main.models import Account, Category, Transaction


class Credit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='credits', null=True)

    title = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.amount}"
from django.core.exceptions import ValidationError
from django.db import models, transaction

from main.models import Account, Category


class Casino_Transaction(models.Model):
    WIN = "win"
    LOSE = "lose"
    TRANSACTION_TYPES = [
        (WIN, "Win"),
        (LOSE, "Lose"),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Transaction")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.type} - {self.amount}"

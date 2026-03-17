from django.db import models
from django.contrib.auth.models import User

class PiggyBank(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    goal = models.FloatField(default=0)

    def __str__(self):
        return f"Piggy Bank of {self.user.username}"


class  piggy_transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.amount} at {self.timestamp}"
from django.db import models
from django.contrib.auth.models import User

class PiggyBank(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    goal = models.FloatField(default=0)

    def __str__(self):
        return f"Piggy Bank of {self.user.username}"

# Добавь эту модель вниз
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()  # Сюда будем записывать сумму (например, 100 или -50)
    timestamp = models.DateTimeField(auto_now_add=True) # Время создастся автоматически

    class Meta:
        ordering = ['-timestamp'] # Автоматическая сортировка: новые сверху

    def __str__(self):
        return f"{self.user.username}: {self.amount} at {self.timestamp}"
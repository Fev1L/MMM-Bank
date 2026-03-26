from django.db import models
from django.contrib.auth.models import User


class Credit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.client_name

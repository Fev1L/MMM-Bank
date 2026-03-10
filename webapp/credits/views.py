from django.shortcuts import render
from .models import Credit

def index(request):
    credit = Credit.objects.first()

    context = {
        "credit": credit
    }

    return render(request, "credits/index.html", context)
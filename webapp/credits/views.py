from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Credit


@login_required
def index(request):
    has_active_loan = Credit.objects.filter(
        user=request.user,
        is_active=True
    ).exists()

    return render(request, 'credits/index.html', {
        'has_active_loan': has_active_loan,
    })
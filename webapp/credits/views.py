from django.http import HttpResponse


def credits_list(request):
    return HttpResponse("Credits module working")
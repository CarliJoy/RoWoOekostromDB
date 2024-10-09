from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Anbieter


def startpage(request: HttpRequest) -> HttpResponse:
    context = {
        "count_active": Anbieter.objects.filter(active=True).count(),
    }

    return render(request, "anbieter/startpage.html", context)

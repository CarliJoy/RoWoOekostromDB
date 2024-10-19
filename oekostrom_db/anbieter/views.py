from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Anbieter


def startpage(request: HttpRequest) -> HttpResponse:
    context = {
        "count_active": Anbieter.objects.filter(active=True).count(),
    }

    return render(request, "anbieter/startpage.html", context)


def survey(request: HttpRequest) -> HttpResponse:
    context = {
        "rowo_url": "/mirror" if settings.ROWO_MIRRORING else "/static",
        "teaser": "Fragebogen für Ökostrom GmbH",
    }

    return render(request, "anbieter/survey.html", context)

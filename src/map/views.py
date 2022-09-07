from django.shortcuts import render

from api.models import Country


def index(request):
    countries = Country.objects.exclude(iso2="AQ").order_by("name").values("name", "iso2")
    context = {"countries": countries}

    return render(request, "map/map.html", context)

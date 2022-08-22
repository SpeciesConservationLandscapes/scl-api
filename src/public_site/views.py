from django.shortcuts import render


def index(request):
    return render(request, "public_site/index.html")


def data_access(request):
    return render(request, "public_site/data-access.html")


def other_tools(request):
    return render(request, "public_site/resources.html")

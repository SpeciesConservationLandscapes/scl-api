from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("data-access", views.data_access, name="data_access"),
    path("resources", views.other_tools, name="resources"),
]

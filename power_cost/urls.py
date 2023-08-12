from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_power_cost, name="power_cost"),
]

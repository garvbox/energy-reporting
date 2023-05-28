from django.http import HttpResponse
from django.shortcuts import render

from .helpers.get_power_data import get_device_summaries


# Create your views here.
def get_power_cost(request):
    context = {"device_summaries": get_device_summaries()}
    return HttpResponse(render(request, "power_cost/index.html", context))

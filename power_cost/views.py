from django.http import HttpResponse

from .helpers.get_power_data import get_power_data


# Create your views here.
def get_power_cost(request):
    return HttpResponse(get_power_data())

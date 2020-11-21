from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """
    Luxurious home page
    """
    return render(request, 'zar/info.html', context={'title': 'Home'})

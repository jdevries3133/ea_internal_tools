from django.shortcuts import render

def home(request):
    """
    Luxurious home page
    """
    return render(request, 'zar/info.html', context={'title': 'Home'})

from django.urls import path

from .views import register, verify_ea

urlpatterns = [
    path('', register, name='register'),
    path('verify-ea/', verify_ea, name='verify_ea')
]

from django.urls import path

from .views import (
    register,
    verify_ea,
    gmail_redirect,
    not_verified_yet
)

urlpatterns = [
    path('', register, name='register'),
    path('verify-ea/<slug:slug>/', verify_ea, name='verify_ea'),
    path('gmail-redirect/', gmail_redirect, name='gmail_redirect'),
    path('not-verified-yet/', not_verified_yet, name='not_verified_yet')
]

from django.urls import path

from .views import (
    register,
    verified,
    gmail_redirect,
    not_verified_yet
)

urlpatterns = [
    path('', register, name='register'),
    path('verified/<slug:slug>/', verified, name='verified'),
    path('gmail-redirect/', gmail_redirect, name='gmail_redirect'),
    path('not-verified-yet/', not_verified_yet, name='not_verified_yet')
]

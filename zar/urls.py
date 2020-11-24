from django.urls import path

from .views import (
    file_upload,
    name_match,
    success,
    monitor_progress,
    download_previous_reports,
)

urlpatterns = [
    path('', file_upload, name='file_upload'),
    path('name-match/', name_match, name='name_match'),
    path('monitor-progress/', monitor_progress, name='monitor_progress'),
    path('success/', success, name='success'),
    path('download-previous/', download_previous_reports, name='download_previous')
]


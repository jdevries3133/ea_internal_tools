from django.urls import path

from .views import (
    file_upload,
    name_match,
    monitor_progress,
    download_previous_reports,
    download_direct,
    skip_name_match,
    no_active_meeting_decision_fork,
)

urlpatterns = [
    path('', file_upload, name='file_upload'),
    path('name-match/', name_match, name='name_match'),
    path('monitor-progress/', monitor_progress, name='monitor_progress'),
    path(
        'download-previous/',
        download_previous_reports,
        name='download_previous_reports'
    ),
    path(
        'no-active-meeting/',
        no_active_meeting_decision_fork,
        name='no_active_meeting_decision_fork'
    ),
    path('snm/', skip_name_match, name='skip_name_match'),
    path(
        'report-download-direct/<int:pk>/',
        download_direct,
        name='download_direct'
    ),
]

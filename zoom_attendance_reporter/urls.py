from django.urls import path

from .views import (
    file_upload,
    faq,
    name_match,
    success,
    download_sample_report
)

urlpatterns = [
    path('', file_upload, name='file_upload'),
    path('faq/', faq, name='faq'),
    path('name_match/', name_match, name='name_match'),
    path('success/', success, name='success'),
    path('sample-report/', download_sample_report, name='download_sample_report')
]


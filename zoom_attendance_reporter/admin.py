from django.contrib import admin

from .models import (
    UnknownZoomName,
    MeetingCompletedReport
)

# Register your models here.
admin.site.register(UnknownZoomName)
admin.site.register(MeetingCompletedReport)

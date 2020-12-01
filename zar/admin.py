from django.contrib import admin

from .models import (
    UnknownZoomName,
    MeetingCompletedReport,
    MeetingSetModel,
    RawMeetingData,
    Report,
)

# Register your models here.
admin.site.register(UnknownZoomName)
admin.site.register(MeetingCompletedReport)
admin.site.register(MeetingSetModel)
admin.site.register(RawMeetingData)
admin.site.register(Report)

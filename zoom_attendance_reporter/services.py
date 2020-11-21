from typing import List

from django.contrib.auth import get_user_model
from teacherHelper.zoom_attendance_report import WorkbookWriter, MeetingSet

from .models import MeetingCompletedReport


def make_meeting_set(*, data: List[bytes], user: get_user_model()) -> MeetingSet:
    """
    Instantiate a MeetingSet and save it in request.session. Siphon
    UnknownZoomNames into models.UnknownZoomNames; the user will be
    redirected to a matching view next.

    Note: form has validated that no file is greater than 1 mb, so file.read()
    is safe.
    """
    meeting_set = MeetingSet(data := [str(f.read(), 'utf-8-sig') for f in data])

    # MeetingCompletedReport provides progress to the frontend.
    # Won't work on dev server because it can't handle concurrent request.
    for meeting in meeting_set.process():
        MeetingCompletedReport.objects.create(
            topic=meeting.topic,
            meeting_time=meeting.datetime.date()
        )


    # delete all MeetingCompletedReport objects once processing is finished
    # user will only be fetching them to get updates on processing progress.
    MeetingCompletedReport.objects.filter(owner=user).delete()
    return meeting_set

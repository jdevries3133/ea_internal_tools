from typing import List

from django.contrib.auth import get_user_model
from teacherHelper.zoom_attendance_report import WorkbookWriter, MeetingSet

from .models import MeetingCompletedReport, MeetingSetModel


def make_meeting_set(*,
                     data: List[bytes],
                     user,
                     request) -> list:
    """
    Create a database, store it in the request session.

    Session is stored in the database too, but hopefully this raw meetingset
    will be updated after name matching, so we also store the id in the session
    so that we can come back and update the model after name matching.

    Note: form has validated that no file is greater than 1 mb, so file.read()
    is safe.
    """
    meeting_set = MeetingSet(data := [str(f.read(), 'utf-8-sig') for f in data])

    # MeetingCompletedReport provides progress to the frontend.
    # Won't work on dev server because it can't handle concurrent requests.
    for meeting in meeting_set.process():
        MeetingCompletedReport.objects.create(
            owner=user,
            topic=meeting.topic,
            meeting_time=meeting.datetime.date()
        )

    serializable = meeting_set.get_serializable_data()
    temp_meeting_set_model = MeetingSetModel.objects.create(
        owner=user,
        json=serializable
    )

    request.session['temp_meeting_set_model'] = temp_meeting_set_model.id
    request.session['meeting_set'] = serializable
    request.session['unknown_names'] = meeting_set.unidentifiable

    # delete all MeetingCompletedReport objects. They are only used so that
    # the frontend can request updates during processing.
    MeetingCompletedReport.objects.filter(owner=user).delete()
    return serializable

from typing import List
# services go here
from teacherHelper.zoom_attendance_report import ExcelWriter, MeetingSet


def make_meeting_set(*, data: List[bytes]) -> MeetingSet:
    """
    Instantiate a MeetingSet and save it in request.session. Siphon
    UnknownZoomNames into models.UnknownZoomNames; the user will be
    redirected to a matching view next.

    Note: form has validated that no file is greater than 1 mb, so file.read()
    is safe.
    """
    meetingset = MeetingSet([str(f.read(), 'utf-8-sig') for f in data])
    meetingset.process()
    return meetingset

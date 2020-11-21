from django.contrib.auth import get_user_model
from django.db.models import Count

from .models import MeetingCompletedReport

def meeting_processing_update(*, user: get_user_model()) -> dict:
    """
    Returns the last processed meeting to provide an update to the frontend
    after a post request has been made.
    """
    completed_reports = MeetingCompletedReport.objects.filter(
        owner=get_user_model()).order_by('created').annotate(
            num_completed=Count('id'))
    return {
        'last_completed': completed_reports.last(),
        'num_completed': completed_reports.num_completed
    }

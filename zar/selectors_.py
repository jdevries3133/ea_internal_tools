import logging

from .models import MeetingCompletedReport, MeetingSetModel

logger = logging.getLogger(__name__)

def meeting_processing_update(*, meeting: MeetingSetModel) -> dict:
    """
    Return context for the frontend template where the user is monitoring
    progress.
    """
    num_ahead = MeetingSetModel.objects.filter(
        created__lt=meeting.created,
        is_processed=False
    ).count()
    if not num_ahead:
        processed = MeetingCompletedReport.objects.filter(
            meeting_set_model=meeting
        )
    else:
        processed = []
    # meeting_processing_health_check()
    return {
        'len_queue': num_ahead,
        'processed_meeting_names': [str(m) for m in processed]
    }

def meeting_processing_health_check() -> None:
    """
    Check if meeting processing is still happening. If there are stale
    unprocessed meetings in the queue, send me an email so that I can fix.
    """
    # TODO check
    unhealthy = False  # all is good!
    if unhealthy:
        logger.critical('Meeting processing health check failed')

def user_has_pending_meeting(user) -> bool:
    if MeetingSetModel.objects.filter(owner=user, is_processed=False):
        return True
    return False

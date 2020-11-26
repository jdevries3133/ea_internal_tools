import logging
from typing import List

from teacherHelper.zoom_attendance_report import MeetingSet

from .models import MeetingCompletedReport, MeetingSetModel, RawMeetingData, UnknownZoomName

logger = logging.getLogger(__name__)

def queue_meeting_set(*,
                     data: List[bytes],
                     user) -> None:
    """
    Save raw data, and create an empty MeetingSetModel to signal to the
    worker that it has a MeetingSet to process.
    """
    if MeetingSetModel.objects.filter(owner=user, is_processed=False):
        raise Exception(
            f'{user.email} is creating a new MeetingSet despite already having '
            'a MeetingSet in progress.'
        )
    meeting_set_model = MeetingSetModel.objects.create(owner=user)
    RawMeetingData.objects.bulk_create([
        RawMeetingData(
            meeting_set_model=meeting_set_model,
            data=str(f.read(), 'utf-8-sig'),
        ) for f in data
    ])

def process_meeting_set(*,
                        meeting_set_model: MeetingSetModel,
                        data: List[str]) -> None:
    """
    Take an unprocessed MeetingSet and process it! Will be run by a worker
    separate from the web application.
    """
    # initialize MeetingSet
    meeting_set = MeetingSet(data)

    # process all data, create progress reports during processing.
    for meeting in meeting_set.process():
        report = MeetingCompletedReport.objects.create(
            topic=meeting.topic,
            meeting_time=meeting.datetime.date(),
            meeting_set_model=meeting_set_model,
        )
        logger.debug(f'Processed {report}. MeetingCompletedReport created.')

    # update meeting_set_model now that processing is finished.
    meeting_set_model.json = meeting_set.get_serializable_data()
    meeting_set_model.is_processed = True
    meeting_set_model.needs_name_matching = True
    meeting_set_model.save()

    # cleanup; delete reports now that processing is done
    MeetingCompletedReport.objects.filter(
        meeting_set_model=meeting_set_model
    ).delete()

def apply_user_manual_name_matches(*,
                                   meeting_set_model: MeetingSetModel,
                                   matches: tuple):
    """
    Add user matches to known matches and run processing again.
    """
    data = RawMeetingData.objects.filter(meeting_set_model=meeting_set_model)


def process_matched_names(*, data: dict) -> dict:
    """
    Process form data from the frontend after the user matches zoom names
    with real names.
    """
    provided_name_pairs = {}
    for zoom_name, true_name in data.items():
        # fix weird slash appended to some names
        if zoom_name[-1] == '/':
            zoom_name = zoom_name[:-1]

        if isinstance(true_name, list):
            provided_name_pairs.setdefault(
                zoom_name,
                true_name[0],
            )

    uzm_objs = []
    for k, v in provided_name_pairs:
        uzm_objs.append(UnknownZoomName(
            zoom_name=k,
            real_name=v,
        ))

    UnknownZoomName.objects.bulk_create(uzm_objs)
    return provided_name_pairs

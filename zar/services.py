from uuid import uuid4
from pathlib import Path
import string
import logging
from typing import List

from django.db.models import Q
from django.shortcuts import redirect
from django.core.files import File
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from teacherHelper.zoom_attendance_report import MeetingSet, WorkbookWriter
from openpyxl.writer.excel import save_virtual_workbook

from .models import (
    MeetingCompletedReport,
    MeetingSetModel,
    RawMeetingData,
    UnknownZoomName,
    Report
)

logger = logging.getLogger(__name__)

def queue_meeting_set(*,
                     data: List[bytes],
                     user) -> None:
    """
    Save raw data, and create an empty MeetingSetModel to signal to the
    worker that it has a MeetingSet to process. Filter all non-ascii
    characters.
    """
    if MeetingSetModel.objects.filter(owner=user, is_processed=False):
        raise Exception(
            f'{user.email} is creating a new MeetingSet despite already having '
            'a MeetingSet in progress.'
        )
    meeting_set_model = MeetingSetModel.objects.create(owner=user)
    data_models = []
    for f in data:
        raw = str(f.read(), 'utf-8-sig')
        processed = ''.join(filter(lambda c: c in string.printable, raw))
        data_models.append(RawMeetingData(
            meeting_set_model=meeting_set_model,
            data=processed,
        ))
    RawMeetingData.objects.bulk_create(data_models)

def process_meeting_set(*,
                        meeting_set_model: MeetingSetModel,
                        data: List[str]) -> None:
    """
    Take an unprocessed MeetingSet and process it! Will be run by a worker
    separate from the web application.
    """
    # initialize MeetingSet with all previously provided user matches
    known_matches = {
        m.zoom_name : m.real_name for m in UnknownZoomName.objects.all()
    }
    meeting_set = MeetingSet(data, known_matches=known_matches)
    logger.debug(
        'Initialized MeetingSet with the followign known matches: %(km)s',
        {'km': known_matches}
    )

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
    meeting_set_model.save()

    # cleanup; delete reports now that processing is done
    MeetingCompletedReport.objects.filter(
        meeting_set_model=meeting_set_model
    ).delete()

def repair_broken_state(*, request, user):  # -> django.http.HttpResponseRedirect
    """
    Call this when an attempt to select the single wip report fails. This
    means something went wrong and the state of the user's models is broken.
    We need to reset and try again.
    """
    MeetingSetModel.objects.filter(
        Q(owner=user),
        Q(needs_name_matching=True) | Q(is_processed=False)
    ).update(
        needs_name_matching=False,
        is_processed=True,
    )
    messages.add_message(
        request,
        messages.ERROR,
        'Something went wrong, please try again.'
    )
    logger.error('Report processing abandoned. Something went wrong')
    return redirect('file_upload')

def generate_excel_report(report_pk: str) -> Report:
    """
    Returns Path in the django default_storage where the excel report is.
    """
    ms = MeetingSetModel.objects.get(pk=report_pk)
    meeting_set = MeetingSet.deserialize(ms.json)
    workbook_buf = save_virtual_workbook(
        WorkbookWriter(meeting_set).generate_report()
    )
    cf = ContentFile(workbook_buf)
    path = f'{ms.owner.username}__{ms.created.isoformat()}.xlsx'
    default_storage.save(path, cf)
    report = Report(
        owner=ms.owner,
        meeting_set_model=ms,
    )
    report.report.name = path
    report.save()
    return report

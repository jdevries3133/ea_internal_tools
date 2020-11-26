"""
Views are listed in order of flow.

1. File Upload
2. Monitor Progress or Cancel
3. Name Match
    skip name match
4. Download Reports

Sometimes, a user gets into a spot in the flow they shouldn't be and
ultimately need to decide where to go next. Hence
no_active_meeting_decision_fork

"""

import logging

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.translation import gettext as _
from teacherHelper.zoom_attendance_report import MeetingSet

from .models import MeetingSetModel, UnknownZoomName
from .services import queue_meeting_set, process_matched_names
from .selectors_ import meeting_processing_update, user_has_pending_meeting

logger = logging.getLogger(__name__)

def file_upload(request):
    """
    Upload csv files.
    """
    if user_has_pending_meeting(user=request.user):
        return redirect('monitor_progress')

    class SmallFilesForm(forms.Form):

        file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={
            'multiple': True
        }))

        def __init__(self, *a, **kw):
            # easier to grab raw files before super()
            self.all_files = kw.pop('all_files', [])
            super().__init__(*a, **kw)

        def clean(self):
            super().clean()
            for file in self.all_files:
                if file.size > 1e6:  # 1 mb
                    raise ValidationError(
                        _('CSV should not be larger than 1mb'),
                        code='invalid'
                    )

    if request.method == 'POST':
        form = SmallFilesForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            queue_meeting_set(
                data=request.FILES.getlist('file_field'),
                user=request.user,
            )
            return redirect('monitor_progress')

    form = SmallFilesForm()
    return render(request, 'zar/file_upload.html', {'form': form})

def monitor_progress(request):
    """
    Provide progress reports on very slow MeetingSet.process() method.
    """
    if (
        request.method == 'POST'
    ) and (
        meeting_set_model := user_has_pending_meeting(user=request.user)
    ):
        logger.info('User cancelled meetingset processing')
        messages.add_message(
            request,
            messages.INFO,
            'Meeting has been cancelled.'
        )
        meeting_set_model.delete()
        return redirect('file_upload')

    # fetch work-in-progress meetingset
    try:
        wip = MeetingSetModel.objects.get(
            owner=request.user,
            is_processed=False,
        )
    except (
        MeetingSetModel.DoesNotExist,
        MeetingSetModel.MultipleObjectsReturned
    ):
        if MeetingSetModel.objects.filter(
            owner=request.user,
            is_processed=True,
            needs_name_matching=True,
        ):
            logger.debug('Ready for name matching')
            return redirect('name_match')
        if request.session.get('name_matching_completed'):
            return redirect('download_previous_reports')
        logger.debug('Work-in-progress meetingset does not exist')
        return redirect('no_active_meeting_decision_fork')

    if wip.needs_name_matching and wip.is_processed:
        logger.debug(
            'wip meeting_set_model is processed and needs names matched. '
            'Redirecting...'
        )
        return redirect('name_match')

    request.session['is_processing'] = True
    return render(
        request,
        'zar/waiting_for_processing.html',
        context={**meeting_processing_update(meeting=wip)}
    )

def name_match(request):
    """
    User matches whacky zoom names with real names if they can.
    """
    need_matching = MeetingSetModel.objects.filter(
        owner=request.user,
        is_processed=True,
        needs_name_matching=True,
    )
    if not need_matching:
        logger.debug(
            'User tried to reach name_match view but has no meetings that need '
            'name matching'
        )
        return redirect('no_active_meeting_decision_fork')

    logger.debug(
        f'Proceeding to match missing names for {len(need_matching)} '
        'meeting_set_models'
    )

    if request.method == 'POST':
        meeting_set_model = MeetingSetModel.objects.get(
            owner=request.user,
            is_processed=True,
            needs_name_matching=True
        )
        process_matched_names(
            data=request.POST,
        )
        meeting_set_model.needs_name_matching = False
        meeting_set_model.is_processed = False  # queue for re-processing
        request.session['name_matching_completed'] = True
        return redirect('monitor_progress')
    all_unidentifiable = set()
    request.session['all_unidentifiable'] = all_unidentifiable
    for meeting_set_model in need_matching:
        all_unidentifiable.update(
            MeetingSet.deserialize(
                meeting_set_model.json
            ).all_unidentifiable
        )
    return render(request, 'zar/name_match.html', context={
        'unidentifiable': all_unidentifiable
    })

def skip_name_match(request):
    """
    Process user's skip name match request and redirect to report download.
    """
    MeetingSetModel.objects.filter(
        owner=request.user,
        is_processed=True,
        needs_name_matching=True
    ).update(needs_name_matching=False)
    return redirect('download_previous_reports')

def download_previous_reports(request):
    """
    Re-download reports previously generated.
    """
    return render(request, 'zar/download_previous_report.html')

def no_active_meeting_decision_fork(request):
    """
    If the user tries to access a report processing flow page when they
    have no pending reports, they will be redirected here
    """
    if request.session.get('is_processing'):
        logger.error(
            'User was redirected to decision fork even though they were in the '
            'middle of processing a meeting_set'
        )
    return render(request,'zar/no_active_meeting_decision_fork.html')

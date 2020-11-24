"""
Views are listed in order of flow.

1. File Upload
2. Monitor Progress or Cancel
3. Name Match
4. Success / Download Reports

~ at a later time: download a previous report.
"""

import logging

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.translation import gettext as _

from .models import MeetingSetModel
from .services import queue_meeting_set
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
                request=request
            )
            return redirect('monitor_progress')

    form = SmallFilesForm()
    return render(request, 'zar/file_upload.html', {'form': form})

def monitor_progress(request):
    """
    Provide progress reports on very slow MeetingSet.process() method.
    """
    if request.method == 'POST':
        # TODO cancel meeting
        return render(request, 'zar/waiting_for_processing.html')

    # fetch work-in-progress meetingset
    wip = MeetingSetModel.objects.get(
        owner=request.user,
        is_processed=False,
    )
    if not wip:
        messages.add_message(
            request,
            messages.INFO,
            'You don\'t have any reports that are currently being processed. '
            'Download any reports you\'ve previously generated here.'
        )
        return redirect('file_upload')
    return render(
        request,
        'zar/waiting_for_processing.html',
        context={**meeting_processing_update(meeting=wip)}
    )

def name_match(request):
    """
    User matches whacky zoom names with real names if they can.
    """
    class NameMatch(forms.Form):
        # TODO: make form
        pass

    if request.method == 'POST':
        # TODO: update with matches
        # TODO: generate report
        pass
    unidentifiable = request.session.get('unidentifiable')
    # TODO: render match form
    return render(request, 'zar/name_match.html')

def success(request):
    """
    Allow the user to download their report.
    """
    return JsonResponse({'message': 'success page in progress'})

def download_previous_reports(request):
    """
    Re-download reports previously generated.
    """
    return JsonResponse({'message': 'download previous reports'})

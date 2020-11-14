from django import forms
from django.shortcuts import render

from .forms import SmallFilesForm
from .services import make_meeting_set

def file_upload(request):
    """
    Upload csv files.
    """
    if request.method == 'POST':
        form = SmallFilesForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            meeting_set = make_meeting_set(
                data=[
                    f for f in request.FILES.getlist('file_field')
                ]
            )
            breakpoint()
    form = SmallFilesForm()
    return render(request, 'file_upload.html', {'form': form})

def faq(request):
    """
    Provide some additional information.
    """
    pass

def name_match(request):
    """
    User matches whacky zoom names with real names if they can.
    """
    pass

def success(request):
    """
    Allow the user to download their report.
    """
    pass

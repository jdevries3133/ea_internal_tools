
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages

from .services import request_ea_verification, ea_email_validator

def register(request):
    """
    User can make an account. User will be a non-ea verified user at first.
    An email will be sent to them asking them to verify their account.
    """
    class RegisterForm(UserCreationForm):
        email = forms.EmailField(
            max_length=100,
            help_text="Required",
            required=True,
            validators=[EmailValidator, ea_email_validator]
        )

        class Meta:
            model = User
            fields = ('username', 'email')

    if request.method == 'POST':
        # process form
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            # save and send verification email.
            user = form.save()
            request_ea_verification(user=user)
            return redirect('file_upload')  # TODO: redirect to intermediary page as described in README
        else:
            # render form again, this time with validation errors.
            return render(
                request,
                'authenticate_ea/register.html',
                context={'form': form}
            )
    # for any other method, render a blank form.
    form = RegisterForm()
    return render(request, 'authenticate_ea/register.html', context={'form': form})

def verify_ea(request, slug):
    """
    User verifies that they have an empowerment academy email address by
    clicking on the link sent to their email.
    """

def redirect_unverified(request):
    """
    Middleware will redirect to this page if the user is not a verified EA
    user. It will allow them to request another confirmation email. or go
    to their email.
    """

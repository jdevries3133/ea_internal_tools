from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.validators import EmailValidator
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages

from .services import (
    request_email_verification,
    validate_email_is_ea,
    assign_user_role_from_slug
)

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
            validators=[EmailValidator, validate_email_is_ea]
        )

        class Meta:
            model = get_user_model()
            fields = ('username', 'email')

    if request.method == 'POST':
        # process form
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            # save and send verification email.
            user = form.save()
            request_email_verification(user=user)
            return redirect('gmail_redirect')
        # else, render form again, this time with validation errors.
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
    user = assign_user_role_from_slug(slug=slug)
    login(request, user)
    return render(request, 'authenticate_ea/verify_ea.html', context={
        'redirect_url': settings.LOGIN_REDIRECT_URL
    })

def gmail_redirect(request):
    """
    Show this message before redirecting the user to gmail to look for
    their confirmation email.
    """
    return render(request, 'authenticate_ea/pre_redirect.html')

def not_verified_yet(request):
    """
    Middleware will redirect to this page if the user is not a verified EA
    user. It will allow them to request another confirmation email. or go
    to their email.
    """
    if request.method == 'POST':
        request_email_verification(user=request.user)
        messages.add_message(
            request,
            messages.INFO,
            'New confirmation email has been sent'
        )
        return redirect('gmail_redirect')
        breakpoint()
    return render(request, 'authenticate_ea/unverified.html', context={
        'email': request.user.email
    })

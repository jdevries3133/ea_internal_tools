# Empowerment-Academy-Only AuthenticationMiddleware

>Implement registration such that only users that have been verified to have
>an @empacad.org address can create access resources.

## How to enable

TODO: add this once implemented

Probably will be:

- Apply middleware
- Include urls
- Configure `settings.py`
    - Setup `EA_AUTHENTICATION`
    - `AUTH_USER_MODEL = 'authenticate_ea.models.User'`

## Now, user registration will follow this flow:

```
registration page form requires email and validates that it ends in @empacad.org
user creates account
user redirected to intermediary page:
    "You must confirm your email before using. Redirecting to gmail now."
    (user exits to mail.google.com)

User has been sent email with a verification link
User clicks link
(user returns)
Use comes to password-only login page; enters password again
User is authenticated in that view
User is redirected to path defined in settings (see <a href="#settings">Settings</a>)
```

After completing that flow, anytime the user logs in, the middleware will now
ignore them.

## Users who exit the flow above

If the user tries logging in again while still unconfirmed:

```
Middleware catches request
Middleware redirects user to "holding pen" page
    Explain the predicament
    Let the user request a new verification link
    Give the user a link to gmail for convenience
```

<h1 name="settings">Settings</h1>

App settings are defined in `settings.py` by `EA_AUTHENTICATION`; a `dict`
which may have the following settings:

| Key                           | Value                                         |
|-------------------------------|-----------------------------------------------|
| domain_name: str              | Domain name; necessary for confirmation email |
| filter_mode: str              | Set mode to `'whitelist'` or `'blacklist'`    |
| filter_routes: list           | Apply the filter to these routes.             |

## Middleware Modes

**Whitelist Mode**

In whitelist mode, specify routes the user **CAN** visit, even if they're not
an EA verified authenticated user.

**Blacklist Mode**

In blacklist mode, specify routes the user **CANNOT** visit if they're not an
authenticated and EA-verified user.

**filter routes**

Regular expressions 

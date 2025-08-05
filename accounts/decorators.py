from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def required_access(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='', user_type=None):
    """
    Decorator for views that checks that the logged in user is the selected user_type,
    redirects to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.user_type == user_type and not u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

from hkn.auth.forms import AuthenticationForm
from hkn.auth.forms import PasswordResetForm, PasswordChangeForm
from django import oldforms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from hkn.auth.decorators import login_required
from hkn.auth.utils import LOGIN_URL, REDIRECT_FIELD_NAME

def login(request, template_name='login.html'):
    "Displays the login form and handles the login action."
    manipulator = AuthenticationForm(request)
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if request.POST:
        errors = manipulator.get_validation_errors(request.POST)
        if not errors:
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '://' in redirect_to or ' ' in redirect_to:
                redirect_to = '/accounts/profile/'
            from hkn.auth.utils import login
            login(request, manipulator.get_user())
            request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        errors = {}
    request.session.set_test_cookie()
    return render_to_response(template_name, {
        'form': oldforms.FormWrapper(manipulator, request.POST, errors),
        REDIRECT_FIELD_NAME: redirect_to,
        'site_name': Site.objects.get_current().name,
    }, context_instance=RequestContext(request))

def logout(request, next_page=None, template_name='logged_out.html'):
    "Logs out the user and displays 'You are logged out' message."
    from hkn.auth.utils import logout
    logout(request)
    if next_page is None:
        return render_to_response(template_name, {'title': 'Logged out'}, context_instance=RequestContext(request))
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page or request.path)

def logout_then_login(request, login_url=LOGIN_URL):
    "Logs out the user if he is logged in. Then redirects to the log-in page."
    return logout(request, login_url)

def redirect_to_login(next, login_url=LOGIN_URL):
    "Redirects the user to the login page, passing the given 'next' page"
    return HttpResponseRedirect('%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, next))

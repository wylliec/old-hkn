from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from hkn.indrel.forms import InfosessionRegistrationForm

def send_registration_email(reg):
    from django.core.mail import send_mail
    d = {'reg' : reg}
    subject = render_to_string('indrel/infosession_registration_email_subject.txt', d)
    subject = ''.join(subject.splitlines())
    message = render_to_string('indrel/infosession_registration_email.txt', d)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['hzarka@gmail.com'])
    

def infosession_registration(request):
    if request.POST:
        form = InfosessionRegistrationForm(request.POST)
        if form.is_valid():
            send_registration_email(form.save())
            return HttpResponseRedirect(reverse('indrel-infosession-registration-complete'))
    else:
        form = InfosessionRegistrationForm()
    d = {}
    d['form'] = form
    return render_to_response('indrel/infosession_registration.html', d, context_instance=RequestContext(request))


def infosession_registration_complete(request):
    return render_to_response('indrel/infosession_registration_complete.html', {}, context_instance=RequestContext(request))

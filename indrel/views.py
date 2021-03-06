from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from hkn.indrel.forms import InfosessionRegistrationForm, ResumeBookOrderForm

def send_registration_email(reg, registration_type):
    from django.core.mail import send_mail
    d = {'reg' : reg}
    subject = render_to_string('indrel/%s_registration_email_subject.txt' % (registration_type,), d)
    subject = ''.join(subject.splitlines())
    message = render_to_string('indrel/%s_registration_email.txt' % (registration_type,), d)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['hzarka@hkn.eecs.berkeley.edu'])
    

def infosession_registration(request):
    if request.POST:
        form = InfosessionRegistrationForm(request.POST)
        if form.is_valid():
            send_registration_email(form.save(), "infosession")
            return HttpResponseRedirect(reverse('indrel-infosession-registration-complete'))
    else:
        form = InfosessionRegistrationForm()
    d = {}
    d['form'] = form
    return render_to_response('indrel/infosession_registration.html', d, context_instance=RequestContext(request))


def infosession_registration_complete(request):
    return render_to_response('indrel/infosession_registration_complete.html', {}, context_instance=RequestContext(request))

def resume_book_registration(request):
    if request.POST:
        form = ResumeBookOrderForm(request.POST)
        if form.is_valid():
            send_registration_email(form.save(), "resume_book")
            return HttpResponseRedirect(reverse('indrel-resume-book-registration-complete'))
    else:
        form = ResumeBookOrderForm()
    d = {}
    d['form'] = form
    return render_to_response('indrel/resume_book_registration.html', d, context_instance=RequestContext(request))


def resume_book_registration_complete(request):
    return render_to_response('indrel/resume_book_registration_complete.html', {}, context_instance=RequestContext(request))


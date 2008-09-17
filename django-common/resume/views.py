from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from resume.models import *
from resume.forms import ResumeForm

@login_required
def upload(request):
    if request.POST:
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user.person)
            request.user.message_set.create(message="Resume uploaded successfully")
            form = ResumeForm()
    else:
        form = ResumeForm()
    form.bind_person(request.user.person)
    
    return render_to_response("resume/upload.html", {'form' : form, 'person' : request.user.person}, context_instance=RequestContext(request))

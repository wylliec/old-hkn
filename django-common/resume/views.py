from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from nice_types import semester
from hkn.info.models import Person
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

@user_passes_test(lambda u: u.is_staff)
def missing(request):
    d = {}
    d['officers'] = set(Person.officers.all()) - set([r.person for r in Resume.objects.filter(submitted__gte = semester.current_semester().start_date)])
    d['candidates'] = set(Person.candidates.all()) - set([r.person for r in Resume.objects.filter(submitted__gte = semester.current_semester().start_date)])
    return render_to_response("resume/missing.html", d, context_instance=RequestContext(request))

from collections import defaultdict
def group_resumes(resumes):
    def key(resume):
        return str(resume.person.extendedinfo.grad_semester.year)
    r = defaultdict(list)
    for resume in resumes:
        k = key(resume)
        name = "%s, %s" % (resume.person.last_name.title(), resume.person.first_name.title())
        r[k].append((name, resume))
    for k in r:
        r[k].sort()
    r = r.items()
    r.sort()
    return r

@user_passes_test(lambda u: u.is_staff)
def table_of_contents(request):
    d = {}
    d['resumes'] = group_resumes(Resume.objects.for_current_semester())
    return render_to_response("resume/table_of_contents.html", d, context_instance=RequestContext(request))

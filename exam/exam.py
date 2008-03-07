from hkn.exam.models import *
from hkn.exam.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
import datetime

def exam_from_form_instance(form, request):
    cd = form.cleaned_data    
    e = Exam()
    e.klass = cd['klass']
    e.topics = ""
    e.publishable = False
    e.paper_only = False
    e.is_solution = cd["is_solutions"]
    e.version = cd["version"]
    e.number = cd["number"]
    e.exam_type= cd["exam_type"]
    e.file = None
    
    if request.user.is_anonymous():
        e.submitter = None
    else:
        e.submitter = request.user
            
    e.save_file_file(e.get_exam_filename() + cd["exam_file_extension"], cd['exam_file'].content)
    return e

def submit(request):
    #return render_to_response("exam/submit.html", context_instance=RequestContext(request))
    examForm = ExamForm()  
    if request.POST:
        form = ExamForm(request.POST, request.FILES)
        if form.is_valid():
            e = exam_from_form_instance(form, request)
            e.save()
            return HttpResponseRedirect("/")
    else:
        form = ExamForm()
    

    return render_to_response("exam/submit.html", {"form" : form}, context_instance=RequestContext(request))    
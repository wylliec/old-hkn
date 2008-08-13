from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from ajaxwidgets.widgets import JQueryAutoComplete
import datetime

from hkn.event.models import *
from hkn.tutor.views import get_tutor_miniinfo, get_courses_tutored, get_published_assignments

def main(request):
    d = {}

    events = Event.objects.order_by('-start_time').filter_permissions(request.user)[:4]
    d['today_events'] = events[:1]
    d['week_events'] = events[1:]
    
    d['day'] = datetime.datetime.now().strftime("%A")
    schedule, can_tutor = get_tutor_miniinfo(get_published_assignments(), day=d['day'])
    can_tutor = get_courses_tutored(can_tutor)
    d['schedule'] = schedule
    d['canTutor'] = can_tutor
    
    xfa = JQueryAutoComplete(source=reverse('course.course.course_autocomplete'))
    d['exam_files_autocomplete']= xfa.render(name="course")


    return render_to_response("main/main.html", d, context_instance=RequestContext(request))

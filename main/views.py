from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.flatpages.models import FlatPage
from ajaxwidgets.widgets import JQueryAutoComplete
from django.utils.safestring import mark_safe
import datetime

from hkn.event.models import *
from hkn.event.utils import add_events_metainfo
from hkn.tutor.views import get_tutor_info, get_courses_tutored, get_published_assignments
from hkn.info import infobox

def main(request):
    d = {}

    events = list(Event.objects.order_by('-start_time').filter_permissions(request.user).annotate_rsvp_count()[:4])
    d['today_events'] = events[:1]
    d['week_events'] = events[1:]
    
    d['day'] = datetime.datetime.now().strftime("%A")
    if d['day'] in ("Saturday", "Sunday"):
        d['day'] = "Monday"
    d["tutoring_title"] = "%s's Tutors" % d['day']
    schedule, can_tutor, tutors = get_tutor_info(tutoring_days=[d['day']])
    can_tutor = get_courses_tutored(can_tutor)
    d['schedule'] = schedule
    d['can_tutor'] = can_tutor
    d["infoboxes"] = infobox.tutors(request, tutors)
    
    xfa = JQueryAutoComplete(source=reverse('course-course-autocomplete'))
    d['exam_files_autocomplete']= xfa.render(name="exam_course", value="Search exams")

    d['content'] = mark_safe(FlatPage.objects.get(url="landing-page").content)

    return render_to_response("main/main.html", d, context_instance=RequestContext(request))

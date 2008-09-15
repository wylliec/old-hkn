from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.flatpages.models import FlatPage
from django.utils.safestring import mark_safe
from django.contrib import auth
import datetime

from hkn.event.models import *
from hkn.event.utils import add_events_metainfo
from hkn.tutor.views import get_tutor_info, get_courses_tutored, get_published_assignments, NoTutorScheduleException
from hkn.info import infobox

def main(request):
    d = {}

    events = Event.objects.order_by('start_time').filter_permissions(request.user).annotate_rsvp_count()
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    week = today + datetime.timedelta(7)
    d['today_events'] = events.filter(start_time__gte = today, start_time__lt = tomorrow)
    d['week_events'] = events.filter(start_time__gte = tomorrow, start_time__lt=week)
    
    delta = datetime.timedelta(hours=7)
    d['day'] = (datetime.datetime.now() + delta).strftime("%A")
    if d['day'] in ("Saturday", "Sunday"):
        d['day'] = "Monday"
    d["tutoring_title"] = "%s's Tutors" % d['day']
    try:
        schedule, can_tutor, tutors = get_tutor_info(tutoring_days=[d['day']])
        can_tutor = get_courses_tutored(can_tutor)
        d['schedule'] = schedule
        d['can_tutor'] = can_tutor
        d["infoboxes"] = infobox.tutors(request, tutors)        
    except NoTutorScheduleException, e:
        d['hide_tutoring'] = True
    
    d['content'] = mark_safe(FlatPage.objects.get(url="landing-page").content)

    return render_to_response("main/main.html", d, context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('hkn-landing-page'))

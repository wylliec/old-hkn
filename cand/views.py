from django.contrib.auth.decorators import permission_required 
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from hkn.events.constants import *
from hkn.cand.forms import EligibilityListForm
from hkn.cand import utils
from hkn.cand.constants import *

def portal(request):
    d = {}

    person = request.user.person
    confirmed_events = request.user.rsvp_set.get_confirmed_events(person)

    d['BIGFUN'] = []
    d['FUN'] = []
    d['COMSERV'] = []
    d['DEPSERV'] = []
    d['CANDMAND'] = []
    for e in confirmed_events:
        if e.event_type in d:
            d[e.event_type].append(e)
            
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    week = today + datetime.timedelta(7)
    events = Event.objects.order_by('start_time').filter_permissions(request.user).annotate_rsvp_count()

    d['upcoming_events'] = events.filter(start_time__gte = today, start_time__lt = week)

    rsvps = person.rsvp_set.filter(event__start_time__gte = today, event__start_time__lt = week)

    d['challenges'] = request.user.mychallenges.all()
    d['reqs'] = EVENT_REQUIRED_NUMBER

    for e in d['upcoming_events']:
        if rsvps.filter(event = e):
            e.rsvped = True
        else:
            e.rsvped = False
            
    d['submitted_resume'] = True
    d['completed_survey'] = True
    d['completed_quiz'] = True

    return render_to_response("cand/portal.html", d, context_instance=RequestContext(request))

@permission_required('info.group_vp')
def upload_eligibility_list(request):
    if request.POST:
        form = EligibilityListForm(request.POST)
        if form.is_valid():
            (num_created, num_existed) = form.save_list()
            request.user.message_set.create(message="Eligibility list uploaded successfully; %d created %d existed" % (num_created, num_existed))
            form = EligibilityListForm()
    else:
        form = EligibilityListForm()
    return render_to_response("cand/upload_eligibility_list.html", {'form' : form}, context_instance=RequestContext(request))

@permission_required('info.group_vp')
def process_eligibility_list(request):
    if request.POST:
        if request.POST.get("process", False):
            utils.process_eligibility_list()
            request.user.message_set.create(message="Eligibility list processed; go to admin view")
    return render_to_response("cand/process_eligibility_list.html", context_instance=RequestContext(request))

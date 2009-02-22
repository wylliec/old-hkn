from django.contrib.auth.decorators import permission_required 
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from hkn.event.constants import *
from hkn.cand.forms import EligibilityListForm
from hkn.cand import utils
from hkn.cand.constants import *

def portal(request):
    d = {}

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    week = today + datetime.timedelta(7)

    person = request.user.person
    confirmed_events = person.rsvp_set.get_confirmed_events(person)
    rsvps = person.rsvp_set.filter(event__start_time__gte = today, event__start_time__lt = week)
    
    for event_type in EVENT_TYPE.values():
        if event_type in EVENT_REQUIRED_NUMBER:
            d[event_type] = { 'events' : [],
                              'num_left' : EVENT_REQUIRED_NUMBER[event_type]
                              }
            
    
    for e in confirmed_events:
        d[e.event_type]['events'].append(e)
        d[e.event_type]['num_left'] -= 1
        if d[e.event_type]['num_left'] == 0:
            del d[e.event_type]['num_left']
        
    events = Event.objects.order_by('start_time').filter_permissions(request.user).annotate_rsvp_count()

    d['events'] = events.filter(start_time__gte = today, start_time__lt = week)
    d['challenges'] = person.mychallenges.all()
    d['challenges_left'] = EVENT_REQUIRED_NUMBER['CHALLENGES'] - d['challenges'].count()

    for e in d['upcoming_events']:
        if rsvps.filter(event = e):
            e.rsvped = True
        else:
            e.rsvped = False
            
    d['submitted_resume'] = False
    d['completed_survey'] = False
    d['completed_quiz'] = False

    return render_to_response("cand/portal.html", d, context_instance=RequestContext(request))

def create_challenge_ajax(request):
    if request.POST:
        officer = request.POST['offficer']
        challenge_name = request.POST['challenge_name']
        c = Challenge()
        c.name = challenge_name
        c.candidate = request.user.person
        c.officer = officer
        c.save()
        return "success"

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

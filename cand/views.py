import datetime
from django.contrib.auth.decorators import permission_required 
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import reverse

from hkn.cand.models import ProcessedEligibilityListEntry, Challenge
from hkn.event.models import *
from hkn.event.constants import *
from hkn.cand.forms import EligibilityListForm, CandidateApplicationForm
from hkn.cand.models import CandidateApplication
from hkn.cand import utils
from hkn.cand.constants import *
from request.utils import *
from resume.models import Resume

from nice_types.semester import current_semester

def portal(request):
    d = {}
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    week = today + datetime.timedelta(7)

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    week = today + datetime.timedelta(7)

    person = request.user.person
    #confirmed_events = person.rsvp_set.get_confirmed_events(person)
    #rsvps = person.rsvp_set.filter(event__start_time__gte = today, event__start_time__lt = week)
    rsvps = person.rsvp_set.all()
    
    for event_type in EVENT_TYPE.values():
        if event_type in EVENT_REQUIRED_NUMBER:
            d[event_type] = { 'events' : [],
                              'num_left' : EVENT_REQUIRED_NUMBER[event_type],
                              'rsvp' : [],
                              }
            
    
    #for e in confirmed_events:
    for r in rsvps:
        e = r.event
        if (e.event_type != 'CANDMAND' or e.name.startswith('General Meeting')) and (e.event_type != 'JOB'):
            d[e.event_type]['events'].append(e)
            d[e.event_type]['rsvp'].append(r)
            if 'num_left' in d[e.event_type].keys():
                d[e.event_type]['num_left'] -= 1
                if d[e.event_type]['num_left'] == 0:
                    del d[e.event_type]['num_left']
        
    events = Event.objects.order_by('start_time').filter_permissions(request.user).annotate_rsvp_count()

    d['upcoming_events'] = events.filter(start_time__gte = today, start_time__lt = week)
    d['challenges'] = person.mychallenges.all()
    d['challenges_left'] = EVENT_REQUIRED_NUMBER['CHALLENGES'] - person.mychallenges.exclude(status=False).count()
    if d['challenges_left'] < EVENT_REQUIRED_NUMBER['CHALLENGES']:
        d['at_least_one_challenge'] = 1
        if d['challenges_left'] <= 0:
            d['challenges_left'] = 0

    for e in d['upcoming_events']:
        if rsvps.filter(event = e):
            e.rsvped = True
        else:
            e.rsvped = False
        
    d['surveys'] = person.surveys.all()

    d['submitted_resume'] = Resume.objects.filter(person=person)
    d['completed_survey'] = person.candidateinfo.completed_survey
    d['completed_quiz'] = person.candidateinfo.completed_quiz

    return render_to_response("cand/portal.html", d, context_instance=RequestContext(request))

def create_challenge_ajax(request):
    if request.POST:
        officer = request.POST['officer']
        challenge_name = request.POST['challenge_name']
        c = Challenge()
        c.name = challenge_name
        c.candidate = request.user.person
        c.officer = officer
        c.save()
        return "success"

# This is the one that's actually being used:
def create_challenge(request):
    if request.POST:
        officer_id = request.POST['officer_id']
        challenge_name = request.POST['challenge_name']
	officer_name = request.POST['officer_autocomplete']
	
	# officer is defined here to avoid scoping problems
	officer = False
	officers = Person.all_officers.ft_query(officer_name)
	if len(officers) == 1:
	    officer = officers[0]
	elif len(officers) == 0:
	    request.user.message_set.create(message="Officer not found. Please check your spelling.")
	    return HttpResponseRedirect(reverse('hkn.cand.views.portal'))
	else:
	    for person in officers:
	        if officer_id == str(person.id):
		    officer = person
            if not officer:
	        request.user.message_set.create(message="Name not specific enough. Please check your spelling.")
	        return HttpResponseRedirect(reverse('hkn.cand.views.portal'))
	        
	c = Challenge()
        c.name = challenge_name
        c.candidate = request.user.person
        c.officer = officer
        c.save()
       
        request_confirmation(c, request.user, permission_user=officer.user_ptr)
        request.user.message_set.create(message="Challenge created successfully")
        return HttpResponseRedirect(reverse('hkn.cand.views.portal'))

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

@permission_required('info.group_vp')
def dump_candidate_emails(request, category):
    entries = ProcessedEligibilityListEntry.objects.filter(category__iexact=category.lower())
    return render_to_response("cand/dump_candidate_emails.html", {'entries' : entries},  context_instance=RequestContext(request), mimetype="text/plain")

@permission_required('main.hkn_candidate')
def application(request):
    if request.POST:
        form = CandidateApplicationForm.get_for_person(request.user.person,request.POST)
        if form.is_valid():
            form.save_for_person()
            request.user.message_set.create(message="Application submitted successfully")
            return HttpResponseRedirect(reverse("hkn.cand.views.portal"))
        
    else:
        form = CandidateApplicationForm.get_for_person(request.user.person)

    return render_to_response("cand/application.html", {'form' : form, 'person' : request.user.person}, context_instance=RequestContext(request))

@permission_required('info.group_vp')
def view_applications(request):
    applications = CandidateApplication.objects.select_related('candidateinfo', 'candidateinfo__person').all()
    return render_to_response("cand/view_applications.html", {"apps" : applications}, context_instance=RequestContext(request))

@permission_required('info.group_vp')
def event_confirmation(request):
    if request.POST:
        try:
            r = RSVP()
            r.event = get_object_or_404(Event, pk=int(request.POST['event_id']))
            r.person = get_object_or_404(Person, pk=int(request.POST['candidate_id']))
        except:
            return HttpResponseBadRequest("Invalid input for candidate: " + request.POST)
        r.transport = -1
        r.vp_confirm = True
        r.vp_comment = "RSVP added by the VP"
        r.save()

    today = datetime.date.today()
    d = {}
    events = Event.semester.filter(start_time__lte=today)
    d['events'] = {}
    for e in events:
        d['events'][e.name] = RSVP.objects.get_confirmables_for_event(e)
    return render_to_response("cand/event_confirmation.html", d, context_instance=RequestContext(request))

@permission_required('info.group_vp')
def all_candidates_events(request):
    d = {}
    d['candidates'] = []
    candidates = Person.candidates.order_by('first_name')
    d['event_types'] = EVENT_TYPE.values()
    for candidate in candidates:
        candidate.rsvps = candidate.rsvp_set.all()
        candidate.tallies ={EVENT_TYPE.CANDMAND: {'count': 0, 'completed': False, 'nice_name': 'General', 'order': 0, },
                             EVENT_TYPE.BIGFUN: {'count': 0, 'completed': False, 'nice_name': 'Big Fun', 'order': 1, },
                             EVENT_TYPE.FUN: {'count': 0, 'completed': False, 'nice_name': 'Fun', 'order': 2},
                             EVENT_TYPE.COMSERV: {'count': 0, 'completed': False, 'nice_name': 'Community Service', 'order': 3},
                             EVENT_TYPE.DEPSERV: {'count': 0, 'completed': False, 'nice_name': 'Department Service', 'order': 4 }, }
        #candidate.tallies.sort(key=lambda item:item['order'])

        for r in candidate.rsvps:
            if r.vp_confirm and (r.event.event_type != EVENT_TYPE.CANDMAND or r.event.name.startswith('General Meeting')) and (r.event.event_type != EVENT_TYPE.JOB) and (r.event.event_type != EVENT_TYPE.MISC):
                candidate.tallies[r.event.event_type]['count'] += 1
                if candidate.tallies[r.event.event_type]['count'] >= EVENT_REQUIRED_NUMBER[r.event.event_type]:
                    candidate.tallies[r.event.event_type]['completed'] = True
        d['candidates'].append(candidate)
    return render_to_response("cand/all_candidates_events.html", d, context_instance=RequestContext(request))
    
def candidate_quiz(request):
    if request.POST:
        if request.person.candidateinfo.candidatequiz:
            cquiz = request.person.candidateinfo.candidatequiz
        else:
            cquiz = CandidateQuiz()

        ans = request.POST
        check_q1([ans['q1']], cquiz)
        check_q2([ans['q2']], cquiz)
        check_q3([ans['q3']], cquiz)
        check_q4([ans['q4']], cquiz)
        check_q5([ans['q51'], ans['q52']], cquiz)
        check_q6([ans['q6']], cquiz)
        check_q7([ans['q71'], ans['q72'], ans['q73'], ans['q74'], ans['q75'], ans['q76']], cquiz)
        check_q8([ans['q81'], ans['q82'], ans['q83'], ans['q84']], cquiz)
        check_q9([ans['q91'], ans['q92']], cquiz)
        check_q10([ans['q101'], ans['q102']], cquiz)
        check_q11([ans['q11']], cquiz)
        
        cquiz.save()
        
        return HttpResponseRedirect(reverse('hkn.cand.views.portal'))
    else:
        return render_to_response("cand/candidate_quiz.html", {}, context_instance=RequestContext(request))

def course_survey_signup(request):
    d = {}
    d['klasses'] = Klass.objects.filter(semester=current_semester(), surveyed=True).select_related('course', 'surveyors')
    d['num_surveys'] = NUM_SURVEYS

    if request.POST:
        signed_up = set(request.person.candidateinfo.surveys.values_list('id', flat=True))
        selected = request.POST.getlist('course_signup')
        selected = set(map(lambda x: int(x), selected))
        new_signups = signedup.intersection(selected)
        for s in new_signups:
            k = Klass.objects.get(id=s)
            request.person.candidateinfo.surveys.add(k)
        

    return render_to_response("cand/course_survey_signup.html", d, context_instance=RequestContext(request))
    

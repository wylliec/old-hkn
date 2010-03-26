from django.contrib.auth.decorators import login_required
import datetime
from django.contrib.auth.decorators import permission_required 
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import reverse

from hkn.cand.models import ProcessedEligibilityListEntry, Challenge
from hkn.event.models import *
from hkn.event.constants import *
from hkn.cand.forms import EligibilityListForm, CandidateApplicationForm
from hkn.cand.models import CandidateApplication, CandidateQuiz, CourseSurvey
from hkn.cand import utils
from hkn.cand.constants import *
from hkn.cand.quiz import *
from request.utils import *
from resume.models import Resume
from course.models import Klass

import nice_types.semester
from nice_types.semester import current_semester

import os

@login_required
def portal(request):
    d = {}
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    week = today + datetime.timedelta(7)

    # Get current user's person and all rsvps the person has made 
    person = request.user.person
    rsvps = person.rsvp_set.all()
    
    # Initialize structure for holding each event organized by type
    for event_type in EVENT_TYPE.values():
        if event_type in EVENT_REQUIRED_NUMBER:
            d[event_type] = { 'events' : [],
                              'num_left' : EVENT_REQUIRED_NUMBER[event_type],
                              'rsvp' : [],
                              }
            
    
    # Iterate through all rsvps and fill up structure from above
    for r in rsvps:
        e = r.event
        if (e.event_type != 'CANDMAND' or e.name.startswith('General Meeting')) and (e.event_type != 'JOB') and (e.event_type != 'MISC'):
            d[e.event_type]['events'].append(e)
            d[e.event_type]['rsvp'].append(r)
            if 'num_left' in d[e.event_type].keys() and r.vp_confirm:
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
        
    num_surveys = person.candidateinfo.coursesurvey_set.count()
    if num_surveys > 0:
      d['at_least_one_survey'] = True
    if num_surveys < SURVEYS_REQUIRED:
      d['surveys_left'] = SURVEYS_REQUIRED - num_surveys
    d['surveys'] = []
    for cs in person.candidateinfo.coursesurvey_set.all():
      d['surveys'].append(cs)
    d['surveys'] = person.candidateinfo.coursesurvey_set.all()

    d['submitted_resume'] = Resume.objects.filter(person=person)
    #d['completed_survey'] = person.candidateinfo.completed_survey
    d['completed_quiz'] = person.candidateinfo.completed_quiz
    #d['completed_quiz'] = False

    f=open('/home/kylim/public_html/vp/vp_announcement.txt','r')
    d['announce']=f.read(512)
    f.close()

    d['add_forms']=os.listdir('/home/kylim/public_html/vp/add_forms')

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
    else:
	request.user.message_set.create(message="Error creating challenge. No HTTP POST data detected.")
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
    applications = CandidateApplication.objects.select_related('candidateinfo', 'candidateinfo__person').filter(candidateinfo__candidate_semester=current_semester)
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
    """
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
    """
    d = {}
    d['candidates'] = []
    candidates = Person.candidates.order_by('first_name')
    
    for candidate in candidates:
        rsvps = candidate.rsvp_set.all()
	candidate.events = {}
	candidate.all_events = []
	for event_type in EVENT_TYPE.values():
	    if event_type in EVENT_REQUIRED_NUMBER:
	        candidate.events[event_type] = { 'events' : [],
		                  'count' : 0,
				  'rsvp' : [],
				  'completed' : False
		                  }
        for r in rsvps:
	    if r.vp_confirm:
	        e = r.event
	        if (e.event_type != 'CANDMAND' or e.name.startswith('General Meeting')) and (e.event_type != 'JOB') and (e.event_type != 'MISC'):
                    candidate.events[e.event_type]['events'].append(e)
		    candidate.events[e.event_type]['rsvp'].append(r)
		    candidate.events[e.event_type]['count'] += 1
		    candidate.all_events.append(r)

	for event_type in EVENT_TYPE.values():
	    if event_type in EVENT_REQUIRED_NUMBER:
	        candidate.events[event_type]['completed'] = candidate.events[event_type]['count'] >= EVENT_REQUIRED_NUMBER[event_type]

	candidate.challenges = candidate.mychallenges.all()
	candidate.challenges_count = candidate.mychallenges.filter(status=True).count()
	candidate.challenges_completed = candidate.challenges_count >= EVENT_REQUIRED_NUMBER['CHALLENGES']

	candidate.submitted_resume = Resume.objects.filter(person=candidate)
	candidate.completed_quiz = candidate.candidateinfo.completed_quiz
	if candidate.completed_quiz:
	    candidate.passed_quiz = 11 - candidate.candidateinfo.candidatequiz.score < 2
	d['candidates'].append(candidate)
    return render_to_response("cand/all_candidates_events.html", d, context_instance=RequestContext(request))

@login_required
def candidate_quiz(request):
    if request.POST:
        if request.user.person.candidateinfo.completed_quiz:
            cquiz = request.user.person.candidateinfo.candidatequiz
        else:
            cquiz = CandidateQuiz()

        ans = request.POST
	cquiz.score = 0
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
	cquiz.candidateinfo = request.user.person.candidateinfo 
        
        cquiz.save()

	request.user.person.candidateinfo.completed_quiz = True
	request.user.person.candidateinfo.save()
        
	request.user.message_set.create(message="Quiz submitted")
        return HttpResponseRedirect(reverse('hkn.cand.views.portal'))
    else:
        d = {}
	if request.user.person.candidateinfo.completed_quiz:
	    d['prev_answers'] = request.user.person.candidateinfo.candidatequiz
	else:
	    d['prev_answers'] = CandidateQuiz()
        return render_to_response("cand/quiz.html", d, context_instance=RequestContext(request))

def rescore_quizzes(request):
    quizzes = CandidateQuiz.objects.filter(candidateinfo__candidate_semester=nice_types.semester.current_semester())
    for cquiz in quizzes:
        cquiz.score = 0
        check_q1([cquiz.q1], cquiz)
        check_q2([cquiz.q2], cquiz)
        check_q3([cquiz.q3], cquiz)
        check_q4([cquiz.q4], cquiz)
        check_q5([cquiz.q51, cquiz.q52], cquiz)
        check_q6([cquiz.q6], cquiz)
        check_q7([cquiz.q71, cquiz.q72, cquiz.q73, cquiz.q74, cquiz.q75, cquiz.q76], cquiz)
        check_q8([cquiz.q81, cquiz.q82, cquiz.q83, cquiz.q84], cquiz)
        check_q9([cquiz.q91, cquiz.q92], cquiz)
        check_q10([cquiz.q101, cquiz.q102], cquiz)
        check_q11([cquiz.q11], cquiz)

        cquiz.save()
    return HttpResponseRedirect(reverse('hkn.main.views.main'))

@permission_required('info.group_vp')
def view_quiz_submissions(request):
    d = {}
    d['quizzes'] = CandidateQuiz.objects.filter(candidateinfo__candidate_semester=nice_types.semester.current_semester()).order_by('candidateinfo__person__first_name')
    return render_to_response("cand/view_quiz_submissions.html", d, context_instance=RequestContext(request))

@permission_required('info.group_vp')
def view_quiz(request, quiz_id):
    d = {}
    d['quiz'] = get_quiz(quiz_id)
    return render_to_response("cand/view_quiz.html", d, context_instance=RequestContext(request))

def get_quiz(quiz_id):
    try:
        return CandidateQuiz.objects.get(pk=quiz_id)
    except (CandidateQuiz.DoesNotExist, ValueError):
        return get_object_or_404(CandidateQuiz, slug=quiz_id)

@permission_required('info.group_csec')
def course_survey_admin(request):
  return render_to_response("cand/course_survey_admin.html", context_instance=RequestContext(request))

@permission_required('info.group_csec')
def course_survey_admin_select_classes(request):
  d = {}
  d['klasses'] = Klass.objects.filter(semester=current_semester(), course__department__abbr__regex=r'(COMPSCI|EL ENG)').order_by('course__department__abbr', 'course__integer_number')
  return render_to_response("cand/course_survey_admin_choose_classes.html", d, context_instance=RequestContext(request))

@permission_required('info.group_csec')
def course_survey_select_ajax(request):
  r = get_object_or_404(Klass, pk=request.REQUEST.get("value", ""))
    
  if request.REQUEST:
    action = request.REQUEST.get("action", "remove")
    if action == "add":
      needs_survey = True
    else:
      needs_survey = False
    r.needs_survey = needs_survey
    r.save()
    
  if r.needs_survey == True:
    state = "enabled"
  else:
    state = "disabled"
         
  js = """option_select(%d, "%s");""" % (r.id, state)
  
  return HttpResponse(js, mimetype='application/javascript')

@permission_required('info.group_csec')
def course_survey_admin_manage(request):
  d = {}
  d['klasses'] = Klass.objects.filter(semester=current_semester(), course__department__abbr__regex=r'(COMPSCI|EL ENG)', needs_survey=True).order_by('course__department__abbr', 'course__integer_number')
  return render_to_response("cand/course_survey_admin_manage.html", d, context_instance=RequestContext(request))

@login_required
def course_survey_signup(request):
  person = request.user.person
  if request.POST:
    klasses_signed_up = []
    for name, value in request.POST.items():
      if name.startswith('klass_'):
        klass_id = name.split('_')[1]
        klass = Klass.objects.get(id=klass_id)
        try: 
          # Already signed up for this klass
          CourseSurvey.objects.get(surveyor=person.candidateinfo, klass=klass)
          continue
        except CourseSurvey.DoesNotExist:
          cs = CourseSurvey(surveyor=person.candidateinfo, klass=klass)
          cs.save()

          request_confirmation(cs, request.user, permission=Permission.objects.get(codename="group_csec"))
          klasses_signed_up.append(klass)
    if len(klasses_signed_up) > 0:
      klass_list = ', '.join([klass.course.short_name() for klass in klasses_signed_up])
      request.user.message_set.create(message="Successfully signed up for %s." % klass_list)
    else:
      request.user.message_set.create(message="No classes selected.")

  num_signed_up = person.candidateinfo.coursesurvey_set.count()
  if num_signed_up >= SURVEYS_REQUIRED:
    request.user.message_set.create(message="Already signed up for %d classes." % SURVEYS_REQUIRED)
    return HttpResponseRedirect(reverse('hkn.cand.views.portal'))
  else:
    d = {}
    d['klasses'] = Klass.objects.filter(semester=current_semester(), course__department__abbr__regex=r'(COMPSCI|EL ENG)', needs_survey=True).order_by('course__department__abbr', 'course__integer_number')
    d['surveys_needed'] = max(SURVEYS_REQUIRED - num_signed_up, 0)
    klasses_signed_up = [coursesurvey.klass for coursesurvey in person.candidateinfo.coursesurvey_set.all()]
    for klass in d['klasses']:
      if klass.coursesurvey_set.count() >= MAX_SURVEYORS_PER_KLASS:
        klass.full = True
      if klass in klasses_signed_up:
        klass.signed_up = True
    return render_to_response("cand/course_survey_signup.html", d, context_instance=RequestContext(request))


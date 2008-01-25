# tutoring views
#from hkn.event.models import *
#from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
#from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

from hkn.auth.decorators import *

from hkn.course import models as courses
from hkn.tutor import models as tutor
from hkn.info import models as hknmodels

from hkn.utils import NiceDict
from hkn.utils import NamedList
from hkn.utils import QueryDictWrapper

from hkn.tutor.constants import *



def schedule(request):
    return render_to_response('tutor/schedule.html',
                              basicContext(request),
                              context_instance = RequestContext(request))

# Create your views here.
@login_required
def signup(request, message = False):
    context = basicContext(request)
    context['signup_table_width'] = 600
    context['signup_col_width'] = 100
    context['days'] = TUTORING_DAYS
    context['timeslots'] = TUTORING_TIMES
    
    context['user'] = request.user
    context['message'] = message
    
    #office preference defaults, populated by previous preferences later
    context['prefer_both'] = False
    context['prefer_soda'] = False
    context['prefer_cory'] = False
    
    #initialize using previous time / day availability data
    prev = [] #list of rows.  Each row is list of Strings
    prevAvailabilitiesList = tutor.Availability.objects.filter(
           person=request.user.person,
           season=currentSeason(),
           year=CURRENT_YEAR)
    
    #whether or not we've seen a preference for soda or cory
    seen_soda = False
    seen_cory = False
    
    #set up dictionary of previous availabilities
    prevAvailabilities = NiceDict(defaultValue="")
    for availability in prevAvailabilitiesList:
        prevAvailabilities[availability.slot] = availability.preference
        if availability.atCory():
            seen_cory = True
        if availability.atSoda():
            seen_soda = True
    
    #create each row for "prev"
    for time in context['timeslots']:
        row = NamedList(name=time)
        for day in context['days']:
            slot = tutor.makeSlot(day=day, time=time)
            row.append({"name":slot,
                        "value":prevAvailabilities[slot]})
        prev.append(row)
    
    context['prev'] = prev
    
    #setup office preference info
    if seen_soda:
        if seen_cory:
            context['prefer_both'] = True
        else:
            context['prefer_soda'] = True
    elif seen_cory:
        context['prefer_cory'] = True
    else:
        #by default, show the both option
        context['prefer_both'] = True
    
    
    #TODO setup previously entered classes
    
#    context['debug'] = "prev size is %s, first elem of first row is: %s" % (len(prev), prev[0][0].__repr__())
    
    return render_to_response("tutor/signup.html",
                              context,
                              context_instance = RequestContext(request))

@login_required
def submit_signup(request):
    if request.method != "POST":
        return signup(request, message="Please enter signup information on this form")
    
    info = QueryDictWrapper(request.POST, defaultValue=False)
    
    #set up tuple of offices
    if info["office"] == "Both":
        offices = (SODA, CORY)
    elif info["office"] == "Soda":
        offices = (SODA,)
    elif info["office"] == "Cory":
        offices = (CORY,)
    else:
        return signup(
            request,
            message="Error with form, please re-enter your information")
    
    #grab any old availabilities for this semester/year
    oldAvailabilities = tutor.Availability.objects.filter(
           person=request.user.person,
           season=currentSeason(),
           year=CURRENT_YEAR)
    
    newAvailabilities = []
    #make the new availabilities for this semester/year
    for time in TUTORING_TIMES:
        for day in TUTORING_DAYS:
            slot = tutor.makeSlot(day=day, time=time)
            if info[slot]:
                try:
                    preference = int(info[slot])
                except:
                    return signup(
                                  request,
                                  message="Error with form at position " + slot +", please re-enter your information.  Use only 1, 2, or nothing for time availabilites.")
                if preference not in [1, 2]:
                    return signup(
                                  request,
                                  message="Error with form, please re-enter your information.  Use only 1, 2, or nothing for time availabilites.")
                for office in offices:
                    newAvailabilities.append(
                        tutor.Availability(
                            person=request.user.person,
                            slot=slot,
                            office=office,
                            season=currentSeason(),
                            year=CURRENT_YEAR,
                            preference=preference))
    
    #data is validated, so safe to update database
    oldAvailabilities.delete()
    for availability in newAvailabilities:
        availability.save()
    
    return HttpResponseRedirect('/tutor/signup')
    #return render_to_response("tutor/signup.html", {},  context_instance = RequestContext(request))

@login_required
def view_signups(request):
    context = basicContext(request, {'showAdminLinks':True})
#    context['signup_table_width'] = 1200
#    context['signup_col_width'] = 200
    context['days'] = TUTORING_DAYS
    context['timeslots'] = TUTORING_TIMES
    context['message'] = False
    context['SODA'] = SODA
    context['CORY'] = CORY
    context['score_miss'] = SCORE_MISS_PENALTY
    context['score_office'] = SCORE_CORRECT_OFFICE
    context['score_preferred'] = SCORE_PREFERENCE[1]
    context['score_less_preferred'] = SCORE_PREFERENCE[2]
    context['score_adjacent'] = SCORE_ADJACENT
    
    assignments = tutor.Assignment.objects.filter(
           season=currentSeason(),
           year=CURRENT_YEAR)
    
    if len(assignments) == 0:
        context['version'] = False
    else:
        context['version'] = request.GET.get('version', False)
        if not context['version']:
            #NOTE: this method of finding the max version is stupid, don't know how to do it nice in django
            context['version'] = max([elem.version for elem in assignments])
    
    if context['version']:
        assignments = assignments.filter(version=context['version'])
    else:
        assignments = tutor.Assignments.objects.none() #returns empty result set
    if context['version'] and len(assignments) == 0:
        context['message'] = "No assignments available for specified version"
        context['version'] = False
    
    #Note: select_related(depth=1) will grab all immediately related models by foreign key
    #so it will grab the person at the same time, requiring fewer database hits later
    availabilities = tutor.Availability.objects.select_related(depth=1).filter(
           season=currentSeason(),
           year=CURRENT_YEAR)
    
    if len(availabilities) == 0:
        return HttpResponse("There are no availbilities, must have at least 1 to view schedule")
    
    #Terminology: "slot preference" is {name, preference, assigned} for some particular slot
    
    #set up dictionary of slot ->
    #  [list of soda slot preferences, list of cory slot preferences]
    availabilitiesDict = NiceDict([
       [{"name":"Nobody", "preference":0, "assigned":False},],
       [{"name":"Nobody", "preference":0, "assigned":False},]])
    #Note: this is super inefficient!  This pulls from the person table MANY times, not sure how to preload that info
    #because this isn't RoR /rant
    for availability in availabilities:
        if availability.slot not in availabilitiesDict:
            availabilitiesDict[availability.slot] = [[], []]
        
        if availability.atSoda():
            officeIndex = 0
        if availability.atCory():
            officeIndex = 1
        person = availability.person
        
        availabilitiesDict[availability.slot][officeIndex].append(
            {"name":person.last + ", " + person.first,
             "preference":availability.preference,
             "assigned":False,
             "id": person.id})
        
    #take note of which slots are assigned for the given or latest version, calculate "happiness"
    happiness = {} #full name -> dictionaries of: net, first_choices, second_choices, adjacent, correct_office_count, missing
    #Note: this is super inefficient!  This pulls from the person table MANY times, not sure how to preload that info
    #because this isn't RoR /rant
    for assignment in assignments:
        person = assignment.person
        fullname = person.last + ", " + person.first
        if assignment.slot not in availabilitiesDict:
            assignmentsDict[assignment.slot] = [
                {"name": "Unassigned", "preference":0, "assigned":False},
                {"name": "Unassigned", "preference":0, "assigned":False}]
        if fullname not in happiness:
            happiness[fullname] = {"net":0,
                                   "first_choices":0,
                                   "second_choices":0,
                                   "adjacencies":0,
                                   "correct_office_count":0,
                                   "missing":HOUR_EXCEPTIONS[fullname] | DEFAULT_HOURS}
            happiness[fullname]["net"] = -1 * SCORE_MISS_PENALTY * happiness[fullname]["missing"]
        
        if assignment.atSoda():
            officeIndex = 0
        if assignment.atCory():
            officeIndex = 1
        
        #scan for the preference
        #note: slot_preference is actually a list of 0 or 1 slot preferences
        slot_preference = [x for x in availabilitiesDict[assignment.slot][officeIndex] if x["name"] == fullname]
        if len(slot_preference) == 1:
            happiness[fullname]["correct_office_count"] += 1
            happiness[fullname]["net"] += SCORE_CORRECT_OFFICE
            happiness[fullname]["missing"] -= 1
            if(happiness[fullname]["missing"] >= 0):
                happiness[fullname]["net"] += SCORE_MISS_PENALTY
            else:
                happiness[fullname]["net"] -= SCORE_MISS_PENALTY
        elif len(slot_preference) == 0:
            #check other office
            slot_preference = [x for x in availabilitiesDict[assignment.slot][(officeIndex + 1) % 2] if x["name"] == fullname]
            
            if len(slot_preference) != 1:
                raise "improper availability found for " + fullname +", assignment to slot " + assignment.slot
            #TODO adjust net for bad office choice?
            happiness[fullname]["missing"] -= 1
            if(happiness[fullname]["missing"] >= 0):
                happiness[fullname]["net"] += SCORE_MISS_PENALTY
            else:
                happiness[fullname]["net"] -= SCORE_MISS_PENALTY
        else:
            raise "improper availability found for " + fullname +", assignment to slot " + assignment.slot
        
        slot_preference = slot_preference[0]
        #note: slot_preference is now just a slot preference
        
        slot_preference["assigned"] = True #mark this as the assigned preference
        
        #update happiness according first or second choice
        if slot_preference['preference'] == 1:
            happiness[fullname]['first_choices'] += 1
            happiness[fullname]['net'] += SCORE_PREFERENCE[1]
        elif slot_preference['preference'] == 2:
            happiness[fullname]['second_choices'] += 1
            happiness[fullname]['net'] += SCORE_PREFERENCE[2]
        else:
            raise "invalid preference for " + fullname + ", assignment to slot " + assignment.slot
    
    
    
    info = [] #list of rows.  Each row is list of dictionaries
    #create each row for "info"
    for time in context['timeslots']:
        row = NamedList(name=time)
        for day in context['days']:
            slot = tutor.makeSlot(day=day, time=time)
            #return signup(request, str(availabilitiesDict))
            row.append({"name":slot,
                        "sodaoptions":availabilitiesDict[slot][0],
                        "coryoptions":availabilitiesDict[slot][1]})
        info.append(row)
    
    #convert happiness into a list sturcture so can iterate over it in the template
    happiness_old = happiness
    happiness = []
    total = 0
    for key in happiness_old:
        temp = happiness_old[key]
        temp['name'] = key
        happiness.append(temp)
        total += temp['net']
    context['total_happiness'] = total
    
    context['info'] = info
    context['happiness'] = happiness
    return render_to_response("tutor/view_signups.html",
                              context,
                              context_instance = RequestContext(request))
    
def submit_assignments(request):
    context = basicContext(request)
    info = QueryDictWrapper(request.POST, defaultValue=False)
    
    old_assignments = tutor.Assignment.objects.filter(
           season=currentSeason(),
           year=CURRENT_YEAR)
    
    if len(old_assignments) == 0:
        version = MIN_VERSION
    else:
        #NOTE: this method of finding the max version is stupidly inefficient, don't know how to do it nice in django
        version = max([elem.version for elem in old_assignments]) + 1
    
#    debugcount = 0
    
    new_assignments = []
    
    for day in TUTORING_DAYS:
        for time in TUTORING_TIMES:
            slot = tutor.makeSlot(day=day, time=time)
            for office in [SODA, CORY]:
                officeslot = tutor.makeOfficeSlot(day=day, time=time, office=office)
                #selected_people is a DICTIONARY mapping id to person object
                people_ids = [int(x) for x in info.getlist(officeslot)]
                selected_people = hknmodels.Person.objects.in_bulk(people_ids)
                
                #TODO remove below debug check
                if len(people_ids) != len(selected_people):
                    return HttpResponse("people_ids and selected_people different for officeslot: " + officeslot)
#                debugcount += len(people_ids)
                
                #make assignments
                for person_id in people_ids:
                    new_assignments.append(
                        tutor.Assignment(person=selected_people[person_id],
                                         slot=slot,
                                         office=office,
                                         season=currentSeason(),
                                         year=CURRENT_YEAR,
                                         version=version)
                        )
    
    #no problems so far with assignments, go and save them all:
    for assignment in new_assignments:
        assignment.save()
    
    return HttpResponseRedirect("/tutor/view_signups")
#    return HttpResponse("would have made " + str(debugcount) + " assignments at version " + str(version))

def admin(request):
    return render_to_response('tutor/admin.html',
                              basicContext(request, {'showAdminLinks':True}),
                              context_instance = RequestContext(request))


#helper methods
def basicContext(request, info = {}):
    ret = NiceDict(False, info)
    if request.user.is_authenticated:
        ret['user'] = request.user
    return ret

#returns [semester_name, year] of previous semester of tutoring
def prevSemesterInfo():
    if CURRENT_SEASON_NAME == "Spring":
        return ["Fall", CURRENT_YEAR - 1]
    return ["Spring", CURRENT_YEAR]

#WARNING: currentSeason is cached, may cause problems when updating seasons
CURRENT_SEASON_HOLDER = []
def currentSeason():
    if len(CURRENT_SEASON_HOLDER) == 0:
        CURRENT_SEASON_HOLDER.append(courses.Season.objects.get(name=CURRENT_SEASON_NAME))
    return CURRENT_SEASON_HOLDER[0]
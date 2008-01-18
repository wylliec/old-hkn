# tutoring views
#from hkn.event.models import *
#from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
#from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

from hkn.auth.decorators import *

from hkn.course import models as courses
from hkn.tutor import models as tutor

from hkn.utils import NiceDict
from hkn.utils import NamedList
from hkn.utils import QueryDictWrapper

from hkn.tutor.constants import *

#replace below by reading from some config file
CURRENT_SEASON_NAME = "Spring"
CURRENT_YEAR = 2008
TUTORING_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
TUTORING_TIMES = ("11a-12", "12-1", "1-2", "2-3", "3-4", "4-5")

CURRENT_SEASON = None
def currentSeason():
    CURRENT_SEASON = courses.Season.objects.get(name=CURRENT_SEASON_NAME)
    return CURRENT_SEASON

#returns [semester_name, year] of previous semester of tutoring
def prevSemesterInfo():
    if CURRENT_SEASON_NAME == "Spring":
        return ["Fall", CURRENT_YEAR - 1]
    return ["Spring", CURRENT_YEAR]

# Create your views here.
@login_required
def signup(request, message = False):
    context = NiceDict(defaultValue="")
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
            slot = day + " " + time
            row.append({"name":slot,
                        "value":prevAvailabilities[slot]})
        prev.append(row)
    
    context['prev'] = prev
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
    
    return render_to_response("tutor/signup.html", context,  context_instance = RequestContext(request))

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
            slot = day + " " + time
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
    
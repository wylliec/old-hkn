from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django import forms
from string import atoi

from django.contrib.auth.decorators import *

from course import models as courses
from hkn.tutor import models as tutor
from hkn.info import models as hknmodels

from nice_types import NiceDict
from nice_types import NamedList
from nice_types import QueryDictWrapper

from hkn.tutor.constants import *
from hkn.tutor.scheduler import State, Slot
from hkn.tutor import output
import nice_types.semester

from re import match, search

@permission_required('main.hkn_officer')
def tutor_list(request):
    return HttpResponse(output.output_html(request.POST.get('version', False)))

@permission_required('main.hkn_officer')
def availabilities_table(request):
    avails = tutor.Availability.objects.for_current_semester().order_by('slot').select_related(depth=1)
    context = basicContext(request)
    context['avails'] = avails

    abs_old = tutor.Availability.availabilities_by_slot(person_converter = lambda person: str(person))
    abs = []
    for slot in abs_old:
        row = []
        for d in abs_old[slot]:
            dict = {}
            row.append({'person': d[0], 'slot': slot.day + ' ' + slot.time, 'office':slot.office, 'preference': d[1]})
        abs.append(row)

    context['abs'] = abs
    
    return render_to_response('tutor/availabilities_table.html',
                              context,
                              context_instance = RequestContext(request))

@permission_required('main.hkn_officer')
def signup(request, message = False):
    context = basicContext(request)
    context['MAX_COURSES'] = MAX_COURSES
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
    prevCanTutor = [ct for ct in tutor.CanTutor.objects.filter(
           person=request.user.person).for_current_semester().select_related(depth=1)]
    prevCanTutor.sort()#CanTutor has __cmp__()
    context['prevCanTutor'] = prevCanTutor
    
    #initialize using previous time / day availability data
    prev = [] #list of rows.  Each row is list of Strings
    prevAvailabilitiesList = tutor.Availability.objects.filter(
           person=request.user.person).for_current_semester()
    
    #whether or not we've seen a preference for soda or cory
    seen_soda = False
    seen_cory = False
    
    #set up dictionary of previous availabilities
    prevAvailabilities = NiceDict(defaultValue="")
    for availability in prevAvailabilitiesList:
        prevAvailabilities[availability.slot] = availability.preference
        if availability.at_cory():
            seen_cory = True
        if availability.at_soda():
            seen_soda = True
    
    #create each row for "prev"
    for time in context['timeslots']:
        row = NamedList(name=time)
        for day in context['days']:
            slot = tutor.make_slot(day=day, time=time)
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

@permission_required('main.hkn_officer')
def submit_signup(request):
    if request.method != "POST":
        return signup(request, message="Please enter signup information on this form")
    
    info = QueryDictWrapper(request.POST, defaultValue=False)
    person = request.user.person

    try:
        numCourses = atoi(info["maxNumCourses"])
    except:
        return signup(
            request,
            message="Invalid value for maxNumCourses")
        
    
    if numCourses > MAX_COURSES:
        return signup(
            request,
            message="You may not sign up for more than %d courses. " % (MAX_COURSES) + str(numCourses))
    
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
    
    semester = nice_types.semester.current_semester()
    #grab any old availabilities for this semester/year
    oldAvailabilities = tutor.Availability.objects.filter(
           person=person, semester=semester)
    
    newAvailabilities = []
    #make the new availabilities for this semester/year
    for time in TUTORING_TIMES:
        for day in TUTORING_DAYS:
            slot = tutor.make_slot(day=day, time=time)
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
                            person=person,
                            slot=slot,
                            office=office,
                            semester=nice_types.semester.current_semester(),
                            preference=preference))
    
    #make CanTutor data
    newCanTutors = {}
    #already ensured numCourses is less than MAX_COURSES
    for i in range(numCourses):
        current = False
        course_id = info["course_" + str(i)]
        if not course_id:
            continue
        if course_id.endswith('cur'):
            course_id = course_id[:-3] #take off last 3 chars of course_id to remove 'cur'
            current = True
        else:
            course_id = int(course_id)
        if course_id in newCanTutors:
            return signup(
                          request,
                          message="Error with form, please re-enter your information.  Do not list the same course multiple times.")
        newCanTutors[course_id] = (
            tutor.CanTutor(person=person,
                           course_id=course_id,
                           semester=nice_types.semester.current_semester(),
                           current=current))
    
    #data is validated, so safe to update database
    oldAvailabilities.delete() #delete old ones
    for availability in newAvailabilities:
        availability.save()
    
    #delete old CanTutor entries
    tutor.CanTutor.objects.filter(person=person).for_current_semester().delete()
    for key in newCanTutors:
        newCanTutors[key].save()
    
    return HttpResponseRedirect('/tutor/signup')
    #return signup(request, message="Made CanTutor assignments: " + str(newCanTutors))
    #return render_to_response("tutor/signup.html", {},  context_instance = RequestContext(request))

@permission_required('main.hkn_officer')
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
    context['score_adjacent_same_office'] = SCORE_ADJACENT_SAME_OFFICE
    context['score_adjacent'] = SCORE_ADJACENT
    
    assignments = tutor.Assignment.objects.for_current_semester()
    
    availCounts = {}
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
        assignments = tutor.Assignment.objects.none() #returns empty result set
    if context['version'] and len(assignments) == 0:
        context['message'] = "No assignments available for specified version"
        context['version'] = False
    
    availabilitiesBySlot = tutor.Availability.availabilities_by_slot(
                                               person_converter = lambda x:x)
    
    if len(availabilitiesBySlot) == 0:
        return HttpResponse("There are no availbilities, must have at least 1 to view schedule")
    
    people = {} #dictionary from id to person object
    
    #Terminology: "slot preference" is {name, preference, preferredOffice, assigned}
    #for some particular slot
    
    #set up dictionary of Slot -> list of slot preferences
    availabilitiesDict = NiceDict([{"name":"Nobody", "preference":0, 'preferredOffice':False, "assigned":False, 'id':-1},])
    for slot in availabilitiesBySlot:
        if slot not in availabilitiesDict:
            availabilitiesDict[slot] = []

        for detail in availabilitiesBySlot[slot]:
            person = detail[0]
            people[person.id] = person

            fullname = person.last_name + ", " + person.first_name
            if fullname not in availCounts:
                availCounts[fullname] = .5
            else:
                availCounts[fullname] += .5
            
            preference = detail[1]
            
            to_append = {"name":person.last_name + ", " + person.first_name,
                         "preference":0,
                         "preferredOffice":False,
                         "assigned":False,
                         "id": person.id}
            
            #preferred offices have preference = preference_level - 0.5
            if int(preference) != preference:
                to_append['preference'] = int(preference) + 1
                to_append['preferredOffice'] = True
            else:
                to_append['preference'] = preference
            
            availabilitiesDict[slot].append(to_append)
        
    
    #raise Exception(assignments)
    #raise Exception(people)
    #take note of which slots are assigned for the given or latest version, calculate "happiness"
    happiness = {} #full name -> dictionaries of: net, first_choices, second_choices, adjacent, correct_office_count, missing
    for assignment in assignments:
        person = people[assignment.person_id]
        fullname = person.last_name + ", " + person.first_name
        slot = Slot(tutor.get_day_from_slot(assignment.slot),
                    tutor.get_time_from_slot(assignment.slot),
                    assignment.office)
        
        if fullname not in happiness:
            happiness[fullname] = {"net":0,
                                   "first_choices":0,
                                   "second_choices":0,
                                   "adjacencies":0,
                                   "same_office_adjacencies":0,
                                   "correct_office_count":0,
                                   "missing":HOUR_EXCEPTIONS[person.id] or DEFAULT_HOURS}
            happiness[fullname]["net"] = -1 * SCORE_MISS_PENALTY * happiness[fullname]["missing"]
        
        #scan for the preference
        slot_preferences = [x for x in availabilitiesDict[slot] if x["name"] == fullname]
        if len(slot_preferences) == 1:
            slot_preference = slot_preferences[0]
            if slot_preference['preferredOffice']:
                #bonus for correct office
                happiness[fullname]["correct_office_count"] += 1
                happiness[fullname]["net"] += SCORE_CORRECT_OFFICE
                
            #no penalty for bad office
            
            happiness[fullname]["missing"] -= 1
            if(happiness[fullname]["missing"] >= 0):
                happiness[fullname]["net"] += SCORE_MISS_PENALTY
            else:
                happiness[fullname]["net"] -= SCORE_MISS_PENALTY
            
            slot_preference["assigned"] = True #mark this as an assigned preference
            #update happiness according first or second choice
            if slot_preference['preference'] == 1:
                happiness[fullname]['first_choices'] += 1
                happiness[fullname]['net'] += SCORE_PREFERENCE[1]
            elif slot_preference['preference'] == 2:
                happiness[fullname]['second_choices'] += 1
                happiness[fullname]['net'] += SCORE_PREFERENCE[2]
            else:
                return HttpResponse( "invalid preference for " + fullname + ", assignment to slot " + assignment.slot)
        else:
            #return HttpResponse( "missing availability found for " + fullname +", assignment to slot " + assignment.slot)
            happiness[fullname]['net'] -= SCORE_MISS_PENALTY
            #otherSlot = slot.other_office_slot()
            if slot not in availabilitiesDict:
                availabilitiesDict[slot] = []
            availabilitiesDict[slot].append({'name':fullname, 'preference':False, 'preferredOffice':False, 'assigned':True, 'id':person.id})
            #availabilitiesDict[slot.other_office_slot()].append({'name':fullname, 'preference':0, 'preferredOffice':False, 'assigned':False, 'id':person.id})
        
        
    
    #Go through again and update happiness for adjacencies.
    #Only count something as an adjacency if the person was also assigned to the time just before
    #this one, so we don't double count.
    for assignment in assignments:
        person = people[assignment.person_id]
        fullname = person.last_name + ", " + person.first_name
        slot = Slot(tutor.get_day_from_slot(assignment.slot),
                    tutor.get_time_from_slot(assignment.slot),
                    assignment.office)
        
        earlierSlot = slot.earlier_slot()
        if earlierSlot == None:
            continue
        if 1 == len([x for x in availabilitiesDict[earlierSlot] if x['id'] == person.id and x['assigned']]):
            happiness[fullname]['same_office_adjacencies'] += 1
            happiness[fullname]['net'] += SCORE_ADJACENT_SAME_OFFICE
        elif 1 == len([x for x in availabilitiesDict[earlierSlot.other_office_slot()]
                       if x['id'] == person.id and x['assigned']]):
            happiness[fullname]['adjacencies'] += 1
            happiness[fullname]['net'] += SCORE_ADJACENT
    
    def optionCompare(x, y):
        """
        should x go after y?  is x ~> y?  1 => yes, 0 => maybe, -1 => no
        """
        if x['preference'] < y['preference']:
            return -1
        elif y['preference'] < x['preference']:
            return 1
        
        if y['preferredOffice'] != x['preferredOffice']:
            if y['preferredOffice']:
                return 1
            else:
                return -1
        
        if x['name'] > y['name']:
            return 1
        else:
            return -1
    
    info = [] #list of rows.  Each row is list of dictionaries
    #create each row for "info"
    for time in context['timeslots']:
        row = NamedList(name=time)
        for day in context['days']:
            slot = tutor.make_slot(day=day, time=time)
            corySlotObj = Slot(day, time, CORY)
            sodaSlotObj = Slot(day, time, SODA)
            #return signup(request, str(availabilitiesDict))
            row.append({"name":slot,
                        "sodaoptions":sorted(availabilitiesDict[sodaSlotObj], optionCompare),
                        "coryoptions":sorted(availabilitiesDict[corySlotObj], optionCompare)})
        info.append(row)
    
    #convert happiness into a list sturcture so can iterate over it in the template
    happiness_old = happiness
    happiness = []
    total = 0
    for key in happiness_old:
        temp = happiness_old[key]
        temp['name'] = key
        idx = -1
        for i in range(len(happiness)):
            if happiness[i]['net'] < temp['net']:
                idx = i
                break
        if idx < 0:
            happiness.append(temp)
        else:
            happiness.insert(idx, temp)
        total += temp['net']
    context['total_happiness'] = total
    
    context['info'] = info
    context['happiness'] = happiness

    availCounts_old = availCounts
    availCounts = []
    for key in availCounts_old:
        temp = {}
        temp['name'] = key
        temp['count'] = availCounts_old[key]
        idx = -1
        for i in range(len(availCounts)):
            if availCounts[i]['count'] < temp['count']:
                idx = i
                break

        if idx < 0:
            availCounts.append(temp)
        else:
            availCounts.insert(idx, temp)

    context['availCounts'] = availCounts
    
    return render_to_response("tutor/view_signups.html",
                              context,
                              context_instance = RequestContext(request))

@permission_required('main.hkn_officer')
def submit_assignments(request):
    context = basicContext(request)
    info = QueryDictWrapper(request.POST, defaultValue=False)
    
    old_assignments = tutor.Assignment.objects.for_current_semester()
    
    if len(old_assignments) == 0:
        version = MIN_VERSION
    else:
        #NOTE: this method of finding the max version is stupidly inefficient, don't know how to do it nice in django
        version = max([elem.version for elem in old_assignments]) + 1
    
#    debugcount = 0
    
    new_assignments = []
    
    for day in TUTORING_DAYS:
        for time in TUTORING_TIMES:
            slot = tutor.make_slot(day=day, time=time)
            for office in [SODA, CORY]:
                officeslot = tutor.make_office_slot(day=day, time=time, office=office)
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
                                         semester=nice_types.semester.current_semester(),
                                         version=version)
                        )
    
    #no problems so far with assignments, go and save them all:
    for assignment in new_assignments:
        assignment.save()
    
    return HttpResponseRedirect("/tutor/view_signups")
#    return HttpResponse("made " + str(len(new_assignments)) + " assignments at version " + str(version))

@permission_required('info.group_tutor')
def admin(request, message = False):
    exceptions = []
    for e in HOUR_EXCEPTIONS:
        person = hknmodels.Person.objects.get(id=e)
        exceptions.append(["%s %s (%d)" % (person.first_name, person.last_name, person.id),
                           HOUR_EXCEPTIONS[e]])
    if len(exceptions) == 0: exceptions = False
    
    context = basicContext(request, {'showAdminLinks':True,
                                     'DEFAULT_HOURS':DEFAULT_HOURS,
                                     'CURRENT_SEASON_NAME':nice_types.semester.current_semester().season_name.title(),
                                     'CURRENT_YEAR':str(nice_types.semester.current_year()),
                                     'exceptions':exceptions,
                                     'message':message})
    
    if request.method != "POST":
        return render_to_response('tutor/admin.html',
                                  context,
                                  context_instance = RequestContext(request))
    
    info = QueryDictWrapper(request.POST)
    changes = {}
    try:
        if info['newExceptions'] and info['newExceptions'] != '':
            newExceptions = {}
            changes['newExceptions'] = newExceptions
            data = info['newExceptions'].replace(' ', '')
            for pair in data.split(','):
                parts = pair.strip().split('=')
                newExceptions[int(parts[0].strip())] = int(parts[1].strip())
                
        if info['removeExceptions'] and info['removeExceptions'] != '':
            removeExceptions = []
            changes['removeExceptions'] = removeExceptions
            for id in info['removeExceptions'].replace(' ', '').split(','):
                removeExceptions.append(int(id))
        
        #if info['CURRENT_SEASON_NAME'] and info['CURRENT_SEASON_NAME'] != '':
        #    changes['CURRENT_SEASON_NAME'] = info['CURRENT_SEASON_NAME']
        
        #if info['CURRENT_YEAR'] and info['CURRENT_YEAR'] != '':
        #    changes['CURRENT_YEAR'] = int(info['CURRENT_YEAR'])
        
        if info['DEFAULT_HOURS'] and info['DEFAULT_HOURS'] != '':
            changes['DEFAULT_HOURS'] = int(info['DEFAULT_HOURS'])
        
        update_constants(changes)
        return HttpResponse('Changes Successful!<br/><a href=".">return</a>')
    except:
        context['message'] = 'Error with submission'
        return render_to_response('tutor/admin.html',
                                  context,
                                  context_instance = RequestContext(request))
@permission_required('info.group_tutor')
def params_for_scheduler(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/tutor/admin")
    
    randomSeed = request.POST.get('randomSeed', False)
    if randomSeed == '': randomSeed = False
    
    maximumCost = request.POST.get('maximumCost', False)
    if maximumCost == '': maximumCost = False
    
    machineNum = request.POST.get('machineNum', False)
    if machineNum == '': machineNum = False
    
    patience = request.POST.get('patience', False)
    if patience == '': patience = False
    
    text = tutor.Availability.parameters_for_scheduler(
             randomSeed=randomSeed and int(randomSeed),
             maximumCost=maximumCost and int(maximumCost),
             machineNum=machineNum and int(machineNum),
             patience=patience and int(patience))
    return HttpResponse(text, mimetype="text/plain")

@permission_required('info.group_tutor')
def submit_schedule(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/tutor/admin")
    
    data = request.POST.get('schedule', False)
    if not data:
        return HttpResponseRedirect("/tutor/admin")
    
    #remove all \r
    data = data.replace('\r', '')
    
    states = State.parse_into_states(data)
    if len(states) != 1 or not states[0].isGoal():
        return admin(request, 'Incorrect data for schedule.  Be sure you copied\
data exactly as output by the scheduler, and that you only have 1 assignment.')
    
    tutor.Assignment.make_assignments_from_state(states[0])
    
    return HttpResponseRedirect("/tutor/admin")

#helper methods
def basicContext(request, info = {}):
    ret = NiceDict(False, info)
    if request.user.is_authenticated:
        ret['user'] = request.user
    return ret

def update_constants(argDict):
    """
    Edit the constants file according to the arguments passed in.
    
    newExceptions should be a dictionary from person_id -> hours to tutor
    removeExceptions should be a list of person_ids to remove
    anything else should be an upper-cased constant name and it's new value
        example:
            update_constants({'newExceptions': {319:3, 18:4},
                             'removeExceptions': [13, 15, 152],
                             'DEFAULT_HOURS': 1,
                             'CURRENT_SEASON_NAME': "Fall"})
    """
    constsFile = open('tutor/constants.py', 'r')
    text = constsFile.read() #read the whole file
    constsFile.close()
    
    newText = ''
    
    inAutomanagedSection = False
    inExceptions = False
    for line in text.split('\n'):
        if line == '#BEGIN AUTOMANAGED':
            inAutomanagedSection = True
            newText += line + '\n'
            continue
        elif line == '#END AUTOMANAGED':
            inAutomanagedSection = False
            newText += line + '\n'
            continue
        
        if not inAutomanagedSection:
            newText += line + '\n' #just copy it to newText
            continue
        else:
            if line == '#BEGIN EXCEPTIONS':
                inExceptions = True
                newText += line + '\n'
                #add any new exceptions to the top
                if 'newExceptions' in argDict:
                    for person_id in argDict['newExceptions']:
                        newText += "%s: %s,#DO NOT EDIT THIS\n" % (person_id,
                               argDict['newExceptions'][person_id])
                continue
            elif line == '#END EXCEPTIONS':
                inExceptions = False
                newText += line + '\n'
                continue
            if line[0] == '#':
                newText += line + '\n' #ignore lines of comments
                continue
            elif inExceptions:
                #see if we should remove an exception, or leave it alone
                if 'removeExceptions' in argDict:
                    parts = line.split(':')
                    if int(parts[0]) in argDict['removeExceptions']:
                        #do not include this exception
                        continue
                    newText += line + '\n' #keep this exception
                    continue
            else:
                parts = line.split(' ')
                variable = parts[0]
                if variable in argDict:
                    val = argDict[variable]
                    if str(val) == val:
                        val = "'%s'" % val #make sure we have quotes for strings
                    newText += "%s = %s #DO NOT EDIT THIS\n" % (variable, val)
                    continue
                else:
                    newText += line + '\n' #keep this assignment
                    continue
    
    #remove any excessive newlines from the end of the file.  They're annoying.
    while newText.endswith('\n\n') or newText.endswith('\r\r') or newText.endswith('\r\n\r\n'):
        newText = newText[:-1]
    
    constsFile = open('tutor/constants.py','w+') #truncates the file
    constsFile.write(newText)
    constsFile.close()

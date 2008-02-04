#tutoring models
from django.db import models
from hkn.course import models as courses
from hkn.info.models import Person
from hkn.tutor.constants import *
import hkn.tutor.scheduler as scheduler

import time

# Create your models here.

#Models pertaining to tutoring signups

class Availability(models.Model):
    """ Models a person's time and office availability for a given season/year. """
    
    person = models.ForeignKey(Person)
    slot = models.CharField(maxlength = 30)
    office = models.CharField(maxlength = 5, choices = (OFFICE_CHOICES)) #Soda or Cory
    season = models.ForeignKey(courses.Season)
    year = models.PositiveIntegerField()
    preference = models.IntegerField()

    def at_cory(self):
        return self.office == "Cory"
    def at_soda(self):
        return self.office == "Soda"
    
    def availabilities_by_slot(seasonName = CURRENT_SEASON_NAME, year = CURRENT_YEAR,
                               person_converter = lambda person:'%d%s%s' %
                                           (person.id, person.first.split(' ')[0], person.last[0])):
        """
        turns availabilities into an availabilitiesBySlot mapping from a Slot object to
        a list of preference details.  A preference detail is a list of [person representation, preference*]
        
        preference* is the preference level, reduced by 0.5 if it is in a preferred office.
        
        Lower preference is always better
        
        person_converter is a method that takes a person and stores it however you want to
        in the returned dictionary.  By default it stores a person as a string with parts:
          [id][first word of first name][first letter of last name]
        """
        season = courses.Season.objects.get(name__iexact=seasonName)
        
        availabilities = Availability.objects.select_related(depth=1).filter(
           season=season,
           year=year)
        
        availabilitiesBySlot = NiceDict([])
        
        for availability in availabilities:
            slot = scheduler.Slot(get_day_from_slot(availability.slot),
                                      get_time_from_slot(availability.slot),
                                      availability.office)
            
            prev = availabilitiesBySlot[slot]
            if len(prev) == 0:
                #create new empty list instance to store info
                prev = []
                availabilitiesBySlot[slot] = prev
            
            person = availability.person
            
            prev.append([person_converter(person),
                         availability.preference - 0.5])
        
        #change preferences in availabilitiesBySlot to account for preferred offices
        for slot in availabilitiesBySlot:
            otherSlot = slot.other_office_slot()
            for detail in availabilitiesBySlot[slot]:
                #check if this person already has a preference detail in the other office
                found = False
                for otherSlotDetail in availabilitiesBySlot[otherSlot]:
                    if otherSlotDetail[0] == detail[0]:
                        found = True
                        break
                if not found:
                    #no detail found for this person.  They must not prefer the other slot
                    availabilitiesBySlot[otherSlot].append([detail[0], int(detail[1] + 0.5)])
        
        return availabilitiesBySlot
    
    availabilities_by_slot = staticmethod(availabilities_by_slot)
    
    def parameters_for_scheduler(seasonName = CURRENT_SEASON_NAME,
                                 year = CURRENT_YEAR,
                                 randomSeed = False,
                                 maximumCost = False,
                                 machineNum = False):
        """
        Returns info (string) to be used by scheduler to generate a schedule.
        May provide a randomSeed and an upper bound guess for the maximumCost.
        """
        
        availabilitiesBySlot = Availability.availabilities_by_slot(seasonName=seasonName,
                                                                   year=year)
        
        ret = "#HKN Mu Chapter parameters for tutoring schedule generator\n"
        ret +='#Generated for %s %s at %s\n' % (seasonName,
                                                year,
                                                time.strftime('%c'))
        ret +="#To use this data, put it into a file parameters.py in the same\n"
        ret +="#location as hkn.tutor.scheduler.  Run scheduler.generate_from_file()\n"
        ret += '\n'
        
        ret += 'options = %s\n' % {'randomSeed':randomSeed, 'maximumCost':int(maximumCost), 'machineNum':machineNum}
        
        ret += 'CORY = "%s"\n' % CORY
        ret += 'SODA = "%s"\n' % SODA
        ret += 'TUTORING_DAYS = %s\n' % (TUTORING_DAYS,)
        ret += 'TUTORING_TIMES = %s\n' % (TUTORING_TIMES,)
        ret += 'SCORE_CORRECT_OFFICE = %d\n' % (SCORE_CORRECT_OFFICE,)
        ret += 'SCORE_MISS_PENALTY = %d\n' % (SCORE_MISS_PENALTY,)
        ret += 'SCORE_PREFERENCE = %s\n' % (SCORE_PREFERENCE,)
        ret += 'SCORE_ADJACENT = %d\n' % (SCORE_ADJACENT,)
        ret += 'SCORE_ADJACENT_SAME_OFFICE = %d\n' % (SCORE_ADJACENT_SAME_OFFICE,)
        ret += 'DEFAULT_HOURS = %s\n' % (DEFAULT_HOURS,)
        
        exceptions = {}
        for person_id in HOUR_EXCEPTIONS:
            person = Person.objects.get(id=person_id)
            identifier = str(person.id) + person.first.split(' ')[0] + person.last[0]
            exceptions[identifier] = HOUR_EXCEPTIONS[person_id]
        ret += 'exceptions = %s\n' % exceptions
        ret += 'defaultHours = %d\n' % DEFAULT_HOURS
        
        scoring = {"correct_office":SCORE_CORRECT_OFFICE,
                   "miss_penalty":SCORE_MISS_PENALTY,
                   "adjacent":SCORE_ADJACENT,
                   "adjacent_same_office":SCORE_ADJACENT_SAME_OFFICE,
                   "preference":SCORE_PREFERENCE}
        ret += 'scoring = %s\n' % scoring
        
        ret += '\n'
        
        for office in (CORY, SODA):
            ret += office.lower() + 'Times = "'
            firstHour = True
            for hour in TUTORING_TIMES:
                if firstHour:
                    firstHour = False
                else:
                    ret += '\\n' #want to have the newline character in the string, not file
                
                firstDay = True
                for day in TUTORING_DAYS:
                    if firstDay:
                        firstDay = False
                    else:
                        ret += ','
                    
                    slot = scheduler.Slot(day, hour, office)
                    firstDetail = True
                    for detail in availabilitiesBySlot[slot]:
                        if firstDetail:
                            firstDetail = False
                        else:
                            ret += ' '
                        
                        ret += detail[0]
                        ret += str(int(detail[1] + 0.5)) #adds the rounded up integer as a string
                        if int(detail[1]) != detail[1]:
                            ret += 'p'
                    #end for detail
                #end for day
            #end for hour
            ret += '"\n' #end quote for office string
        
        return ret
    
    parameters_for_scheduler = staticmethod(parameters_for_scheduler)
    
    
class Assignment(models.Model):
    """ Models when a person will tutor for a given season/year and schedule version. """
    
    person = models.ForeignKey(Person)
    slot = models.CharField(maxlength = 30)
    office = models.CharField(maxlength = 5, choices = (OFFICE_CHOICES)) #Soda or Cory
    season = models.ForeignKey(courses.Season)
    year = models.PositiveIntegerField()
    
    version = models.PositiveIntegerField()
    """
    Allows multiple schedule versions to be generated and saved
    for a single season/year.
    """

    def at_cory(self):
        return self.office == "Cory"
    def at_soda(self):
        return self.office == "Soda"
    
    def get_max_version(seasonName = CURRENT_SEASON_NAME, year = CURRENT_YEAR, season = False):
        """
        NOTE: this is REALLY INEFFICIENT!
        gets the max version of all assignments for given year and season name
        """
        season = season or courses.Season.objects.get(name__iexact = seasonName)
        assigns = Assignment.objects.filter(season=season, year=year)
        if len(assigns) == 0:
            return MIN_VERSION - 1
        return max([x.version for x in assigns])
    get_max_version = staticmethod(get_max_version)
    
    def make_assignments_from_state(state, seasonName = CURRENT_SEASON_NAME, year = CURRENT_YEAR):
        """
        convert a state into assignments.  Expects that each value in state is a string
        prefixed with a valid person id.
        """
        
        assignments = []
        
        season = courses.Season.objects.get(name__iexact = seasonName)
        
        version = Assignment.get_max_version(year=year, season=season) + 1
        
        for slot in state:
            person_id = get_integer_prefix(state[slot])
            assignments.append(Assignment(person_id=person_id,
                                          slot=make_slot(slot.day, slot.time),
                                          office=slot.office,
                                          season=season,
                                          year=year,
                                          version=version))
        
        #all assignments created successfully, so save them
        for a in assignments:
            a.save()
        
        return
    
    make_assignments_from_state = staticmethod(make_assignments_from_state)
    

class CanTutor(models.Model):
    """ Models who can tutor what for a particular season/year. """
    
    person = models.ForeignKey(Person)
    course = models.ForeignKey(courses.Course)
    season = models.ForeignKey(courses.Season)
    year = models.PositiveIntegerField()
    current = models.BooleanField()
    


#Models pertaining to tutoring attendance

class Attendance(models.Model):
    """ Models one of the academic departments. """
    
    person = models.ForeignKey(Person)
    """ TODO: need to auto-assign to "Anonymous" person when blank """
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    repeat = models.BooleanField()
    """ If we are certain that a tutee has come before, set repeat to true """
    
class CourseTutored(models.Model):
    """ Models a course tutored to a tutee during a particular attendance """
    attendance = models.ForeignKey(Attendance)
    course = models.ForeignKey(courses.Course)
    topics = models.CharField(maxlength = 150)
    """ Description of topics tutored """



#Helpful methods
def make_slot(day="BAD_DAY", time="BAD_TIME"):
    return day + ' ' + time
def get_day_from_slot(slot):
    return slot.split(' ')[0]
def get_time_from_slot(slot):
    return slot.split(' ')[1]
def make_office_slot(day="BAD_DAY", time="BAD_TIME", office="BAD_OFFICE"):
    return day + ' ' + time + ' ' + office
def get_day_from_office_slot(officeSlot):
    return officeSlot.split(' ')[0]
def get_time_from_office_slot(officeSlot):
    return officeSlot.split(' ')[1]
def get_office_from_office_slot(officeSlot):
    return officeSlot.split(' ')[2]
def get_integer_prefix(string):
    temp = ''
    for char in string:
        if char in ['0','1','2','3','4','5','6','7','8','9']:
            temp += char
        else:
            break
    if temp == '':
        raise ValueError("no integer prefix!")
    return int(temp)

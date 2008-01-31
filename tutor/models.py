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
    
    def availabilities_by_slot(seasonName = CURRENT_SEASON_NAME,
                               year = CURRENT_YEAR):
        
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
            
            #person is stored as str(id) + first word of first name + first letter of last name
            prev.append([str(person.id) + person.first.split(' ')[0] + person.last[0],
                         availability.preference])
        
        #change preferences in availabilitiesBySlot to account for preferred offices
        for slot in availabilitiesBySlot:
            otherSlot = slot.otherOfficeSlot()
            for detail in availabilitiesBySlot[slot]:
                #check if this person already has a preference detail in the other office
                found = False
                for otherSlotDetail in availabilitiesBySlot[otherSlot]:
                    if otherSlotDetail[0] == detail[0]:
                        found = True
                        break
                if not found:
                    #no detail found for this person.  They must not prefer the other slot
                    availabilitiesBySlot[otherSlot].append([detail[0], detail[1]])
                
                #note that this slot is preferred
                detail[1] -= 0.5
        
        return availabilitiesBySlot
    
    availabilities_by_slot = staticmethod(availabilities_by_slot)
    
    def parameters_for_scheduler(seasonName = CURRENT_SEASON_NAME,
                                 year = CURRENT_YEAR,
                                 randomSeed = False,
                                 maximumCost = False):
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
        
        ret += 'options = %s\n' % {'randomSeed':randomSeed, 'maximumCost':maximumCost}
        
        exceptions = {}
        for person_id in HOUR_EXCEPTIONS:
            person = Person.get(id=person_id)
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
    
    def get_max_version(seasonName = CURRENT_SEASON_NAME, year = CURRENT_YEAR):
        """
        NOTE: this is REALLY INEFFICIENT!
        gets the max version of all assignments for given year and season name
        """
        season = courses.Season.objects.get(name=seasonName)
        return max([x.version for x in Assignment.objects.filter(season=season, year=year)])
    get_max_version = staticmethod(get_max_version)
    

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
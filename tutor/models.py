#tutoring models
from django.db import models
from hkn.course import models as courses
from hkn.info.models import Person
from hkn.tutor.constants import *

import scheduler

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
    
    def generate_schedule(seasonName = CURRENT_SEASON_NAME, year = CURRENT_YEAR, randomSeed = False):
        """
        Generate a new schedule given latest assignments to given season name and year
        May also provide a randomSeed
        
        Returns happiness info for each person
        """
        options = NiceDict(False, {'random_seed':randomSeed})
        
        season = courses.Season.objects.get(name=seasonName)
        version = Assignments.getMaxVersion(seasonName=seasonName, year=year) + 1
        
        availabilities = tutor.Availability.objects.select_related(depth=1).filter(
           season=season,
           year=year)
        
        availabilitiesBySlot = NiceDict([])
        
        for availability in availabilities:
            slotInfo = {"day":get_day_from_slot(availability.slot),
                    "time":get_time_from_slot(availability.slot),
                    "office":availability.office}
            
            prev = availabilitiesBySlot[slotInfo]
            if len(prev) == 0:
                #create new empty list instance to store info
                prev = []
                availabilitiesBySlot[slotInfo] = prev
            
            prev.append({"person": availability.person,
                         "preference":availability.preference})
        
        #delegate all calculation work to the scheduler
        schedule_info = scheduler.generate_schedule(availabilitiesBySlot=availabilitiesBySlot,
                                              options=options)
        
        #set up assignment objects
        new_assignments = []
        assignmentsDict = schedule_info['assignments']
        for slotInfo in assignmentsDict:
            slotname = make_slot(day=slotInfo['day'], time=slotInfo['time'])
            new_assignments.append(
                Assignment(person=assignmentsDict[slotInfo]['person'],
                           slot=slotname,
                           office=slotInfo['office'],
                           season=season,
                           year=year,
                           version=version)
                           )
        
        #save assignment objects
        for elem in new_assignments:
            elem.save()
        
        #return
        return schedule_info['happiness']
        
    generate_schedule = staticmethod(generate_schedule)

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
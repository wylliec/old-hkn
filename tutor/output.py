from hkn import semester

from hkn.utils import NiceDict
from hkn.tutor.constants import *
from hkn.tutor import models as tutormodel
from hkn.course import models as coursemodel
from hkn.info import models as infomodel


def output_html():

    def day_abbrev(day):
        return day[0:2]
    
    def military_time(time):
        offset = 12
        if time[-1] == "a":
            offset = 0
            time = time[0:-1]
        if time == "12":
            offset = offset - 12
        time = int(time) + offset
        if time < 10:
            return "0" + str(time) + "00"
        return str(time) + "00"
    
    startTime = military_time(TUTORING_TIMES[0].split("-")[0])
    endTime = military_time(TUTORING_TIMES[-1].split("-")[1])

    HTML_STRING = ""
    
#    Output semester and office hours information
    HTML_STRING += "SEMESTER " + CURRENT_SEASON_NAME + " " + str(CURRENT_YEAR) + "\n"
    HTML_STRING += "CORYSTART " + startTime + "\n"
    HTML_STRING += "CORYEND " + endTime + "\n"
    HTML_STRING += "SODASTART " + startTime + "\n"
    HTML_STRING += "SODAEND " + endTime + "\n"
    HTML_STRING += "INTERVAL 60"
    
#    Obtain the list of current tutors and output their tutoring availability to the file
    seasonID = coursemodel.Season.objects.get(name = CURRENT_SEASON_NAME.lower()).id
    people = infomodel.Person.objects.all()
    for person in people:
        personID = person.id
        availabilities = tutormodel.Availability.objects.filter(person = personID, season = seasonID, year = CURRENT_YEAR)
        if len(availabilities) == 0:
            continue
        tutors = tutormodel.CanTutor.objects.filter(person = personID, season = seasonID, year = CURRENT_YEAR)

        HTML_STRING += "\n\nBEGINTUTOR\n"
        
#        Output tutor name
        person = infomodel.Person.objects.get(id = personID)
        HTML_STRING += "NAME " + person.name() + "\n"
        
#        Output available times by location
        coryTimes = "CORYTIMES"
        sodaTimes = "SODATIMES"
        for availability in availabilities:
            slotDay = day_abbrev(tutormodel.get_day_from_slot(availability.slot))
            print tutormodel.get_time_from_slot(availability.slot)
            slotTime = military_time(tutormodel.get_time_from_slot(availability.slot).split("-")[0])
            if availability.office == CORY:
                coryTimes = coryTimes + " " + slotDay + slotTime
            if availability.office == SODA:
                sodaTimes = sodaTimes + " " + slotDay + slotTime
        HTML_STRING += coryTimes + "\n"
        HTML_STRING += sodaTimes + "\n"
        
#        Output tutor's courses
        courseList = "CLASSES"
        for tutor in tutors:
            course = tutor.course
            true_dept_abbr = course.department_abbr
            preferred_dept_abbr = coursemodel.Department.nice_abbr(true_dept_abbr)
            courseList = courseList + " " + preferred_dept_abbr + course.number
        HTML_STRING += courseList + "\n"
        
        HTML_STRING += "ENDTUTOR"
    return HTML_STRING
    """
#    Write to file
    FILE = open("schedule.html","w")
    FILE.write(HTML_STRING)
    """
    FILE.close()
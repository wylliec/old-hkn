from nice_types import NiceDict
from hkn.tutor.constants import *
from hkn.tutor import models as tutormodel
from course import models as coursemodel
from hkn.info import models as infomodel
import nice_types.semester


def output_html(version=False):

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
    
    version = version or tutormodel.Assignment.get_max_version()
    
    HTML_STRING = ""
    
#    Output semester and office hours information
    HTML_STRING += "SEMESTER " + nice_types.semester.current_semester().verbose_description() + "\n"
    HTML_STRING += "CORYSTART " + startTime + "\n"
    HTML_STRING += "CORYEND " + endTime + "\n"
    HTML_STRING += "SODASTART " + startTime + "\n"
    HTML_STRING += "SODAEND " + endTime + "\n"
    HTML_STRING += "INTERVAL 60"
    
#    Obtain the list of current tutors and output their tutoring assignments to the file
    people = infomodel.Person.objects.all()
    for person in people:
        personID = person.id
        assignments = tutormodel.Assignment.objects.filter(person = personID, version = version).for_current_semester()
        if len(assignments) == 0:
            continue
        canTutor = tutormodel.CanTutor.objects.filter(person = personID).for_current_semester()

        HTML_STRING += "\n\nBEGINTUTOR\n"
        
#        Output tutor name
        person = infomodel.Person.objects.get(id = personID)
        HTML_STRING += "NAME " + person.first_name.split(' ')[0] + ' ' + person.last_name + "\n"
        
#        Output available times by location
        coryTimes = "CORYTIMES"
        sodaTimes = "SODATIMES"
        for assignment in assignments:
            slotDay = day_abbrev(tutormodel.get_day_from_slot(assignment.slot))
#            print tutormodel.get_time_from_slot(assignment.slot)
            slotTime = military_time(tutormodel.get_time_from_slot(assignment.slot).split("-")[0])
            if assignment.at_cory():
                coryTimes = coryTimes + " " + slotDay + slotTime
            if assignment.at_soda():
                sodaTimes = sodaTimes + " " + slotDay + slotTime
        HTML_STRING += coryTimes + "\n"
        HTML_STRING += sodaTimes + "\n"
        
#        Output tutor's courses
        courseList = "CLASSES"
        for entry in canTutor:
            course = entry.course
            true_dept_abbr = course.department_abbr
            preferred_dept_abbr = coursemodel.Department.get_nice_abbr(true_dept_abbr)
            number = course.number
            #get rid of trailing L or N, like CS61BL and EE20N
            if number[-1].lower() in ('l', 'n'):
                number = number[:-1]
            #move honors or cross-listed prefix to the end, so not confused with department
            if number[0].lower() in ('h', 'c'):
                number = number[1:] + number[0]
            courseList = courseList + " " + preferred_dept_abbr + number
            if entry.current:
                courseList = courseList + "cur"
        HTML_STRING += courseList + "\n"
        
        HTML_STRING += "ENDTUTOR"
    return HTML_STRING
    """
#    Write to file
    FILE = open("schedule.html","w")
    FILE.write(HTML_STRING)
    FILE.close()
    """

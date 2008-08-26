from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext 
from hkn.info.models import Person

def tutors(request, people):
    tutors = []
    for person in people:
        assignments = person.assignment_set.all().latest_version()
        courses_tutored = ", ".join([ct.course.short_name() for ct in person.cantutor_set.for_current_semester().select_related("course").order_by('course__department_abbr', 'course__number')])
        
        d = {}
        d["person"] = person
        d["assignments"] = assignments
        d["courses"] = courses_tutored
        tutors.append(d)
    
    d = {"tutors" : tutors}
    return render_to_string("info/infobox/tutors.html", d, context_instance=RequestContext(request))
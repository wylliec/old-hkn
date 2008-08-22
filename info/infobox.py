from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext 
from hkn.info.models import Person

def tutor(request, person_id, return_string=False, person=None):
    if not person:
        person = get_object_or_404(Person, pk = person_id)
    assignments = person.assignment_set.all().latest_version()
    courses_tutored = ", ".join([ct.course.short_name() for ct in person.cantutor_set.for_current_semester().order_by('course__department_abbr', 'course__number')])

    d = {}
    d["person"] = person
    d["assignments"] = assignments
    d["courses"] = courses_tutored
    
    if return_string:
        return render_to_string("info/infobox/tutor.html", d, context_instance=RequestContext(request))
    else:
        return render_to_response("info/infobox/tutor.html", d, context_instance=RequestContext(request))
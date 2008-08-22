from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext 
from hkn.info.models import Person

def tutor(request, person_id):
    p = get_object_or_404(Person, pk = person_id)
    assignments = p.assignment_set.all().latest_version()
    courses_tutored = ", ".join([ct.course.short_name() for ct in p.cantutor_set.for_current_semester().order_by('course__department_abbr', 'course__number')])

    d = {}
    d["person"] = p
    d["assignments"] = assignments
    d["courses"] = courses_tutored
    
    return render_to_response("info/infobox/tutor.html", d, context_instance=RequestContext(request))

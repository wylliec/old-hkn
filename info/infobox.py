from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext 
from hkn.info.models import Person

def tutor(request, person_id):
    p = get_object_or_404(Person, pk = person_id)
    assignments = p.assignment_set.all().latest_version()

    d = {}
    d["person"] = p
    d["assignments"] = assignments
    return render_to_response("info/infobox/tutor.html", d, context_instance=RequestContext(request))

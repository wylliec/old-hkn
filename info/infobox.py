from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext 
from django.core.cache import cache
from hkn.info.models import Person

def tutors(request, people):
    d = {}    
    tutors = []
    for person in people:
        cache_key = 'tutor_infobox_%d' % person.id
        tutor_infobox = cache.get(cache_key)
        if not tutor_infobox:
            courses_tutored = ", ".join([ct.course.short_name() for ct in person.cantutor_set.for_current_semester().select_related("course").order_by('course__department_abbr', 'course__integer_number')])
            d["person"] = person
            d["assignments"] = person.assignment_set.all().latest_version()
            d["courses"] = courses_tutored            
            tutor_infobox = render_to_string("info/infobox/tutor.html", d)       
            cache.set(cache_key, tutor_infobox, 600)
        tutors.append(tutor_infobox)    
    return "".join(tutors)

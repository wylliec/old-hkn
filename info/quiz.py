from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from hkn.info.models import *
from django.contrib.auth.decorators import *
from string import atoi

#@login_required
#@permission_required("all.view.basic")
@permission_required("all.view.basic")
def quiz(request, person_class):
    persons = None
    if person_class == "all":
        persons = Person.objects.order_by(sort_field)
    elif person_class == "officers":
        persons = Person.officers.order_by(sort_field)
    elif person_class == "candidates":
        persons = Person.candidates.order_by(sort_field)
    elif person_class == "members":
        persons = Person.members.order_by(sort_field)

    paginator = ObjectPaginator(persons, max)
    people = paginator.get_page(page)
    d = { "persons" : people, sort_field_base + "_order" : sort_character, "page_range" : range(paginator.pages), "class" : person_class, "max" : max, "page" : page }
    

    return render_to_response("info/list.html", d, context_instance=RequestContext(request))


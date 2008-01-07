from hkn.cand.models import *
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core import urlresolvers
from django import newforms as forms

from hkn.event.constants import RSVP_TYPE, EVENT_TYPE
from hkn.list import get_list_context, filter_objects
from hkn import semester

import datetime
from string import atoi

def message(request, msg):
    return render_to_response("event/message.html", {"message" : msg},  context_instance = RequestContext(request))

def initiate(request, category = "all"):
    d = get_list_context(request, default_sort = "first", default_category = category)    
    d["objects_url"] = urlresolvers.reverse("hkn.cand.initiate.initiate_ajax")
    return render_to_response("list/list.html", d, context_instance=RequestContext(request))

def get_candidates_for_category(clazz, categories, category_map):
    candidates = Person.candidates.none()

    for category in categories:
        if category == "initiated":
            candidates = candidates | Person.candidates.filter(candidateinfo__initiated = True)
        elif category == "uninitiated":
            candidates = candidates | Person.candidates.filter(candidateinfo__initiated = False)
        elif category == "all":
            candidates = Person.candidates.all()

    return candidates

def add_candidate_initiation_metainfo(candidates):
    for c in candidates:
        c.comment = c.candidateinfo.initiation_comment
        c.events_attended = len(RSVP.objects.getConfirmedEvents(c))
    return candidates		

def initiate_ajax(request):
    list_context = get_list_context(request, default_sort = "first")
    query_people = lambda objects, query: Person.objects.query(query, objects)
    (candidates, pages) = filter_objects(Person, list_context, query_objects = query_people, get_objects_for_categories = get_candidates_for_category, final_filter = add_candidate_initiation_metainfo)

    

    if request.POST:
        for c in candidates:
            attr_initiated = str(c.id) + ".initiated"
            attr_comment = str(c.id) + ".comment"

            if not request.POST.has_key(attr_comment):
                continue

            ci = c.candidateinfo
            ci.initiation_comment = request.POST[attr_comment]
            ci.initiated = request.POST.has_key(attr_initiated)
            ci.save()
        candidates = add_candidate_initiation_metainfo(candidates)    
                        


    list_context["candidates"] = candidates
    list_context["page_range"] = range(1, pages+1)
    

    return render_to_response("cand/ajax/list_initiates.html", list_context, context_instance = RequestContext(request))

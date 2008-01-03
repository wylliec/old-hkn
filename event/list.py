from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers
from hkn.list import get_list_context, filter_objects
from hkn.event.models import *
from string import atoi

def list_events(request, category):
    d = get_list_context(request, default_sort = "-start_time", default_category = category)    
    d["objects_url"] = urlresolvers.reverse("hkn.event.list.list_events_ajax")
    d["extra_body"] = get_template("event/ajax/list_javascript.html").render({})
    return render_to_response("list/list.html", d, context_instance=RequestContext(request))

def filter_events_by_category(clazz, objects, category):
    try:
        objects = objects & clazz.__dict__[category].manager.all()
        return objects;
    except:
        pass
    
    category = category.upper()
    if not EVENT_TYPE.CHOICES_DICT.has_key(category):
        raise KeyError, "category does not exist!"   
    
    return objects.filter(event_type = category)

def get_events_for_categories(clazz, categories, category_map):
    objects = clazz._default_manager.all()
    if len(categories) == 0:
        return objects

    try:        
        for category in categories:
            category = category_map.get(category, category)            
            objects = filter_events_by_category(clazz, objects, category)            
    except KeyError, e:
        raise KeyError, "Category \"" + category + "\" does not exist for class " + clazz.__class__.__name__
    
    return objects

def add_events_metainfo(events):
    for event in events:
        event.num_rsvps = len(event.rsvp_set.all())
    return events

def list_events_ajax(request):
    list_context = get_list_context(request, default_sort = "-start_time")
    permissions = request.user.get_all_permissions()
    filter_permissions = lambda objects: objects.filter(view_permission__in = permissions)
    query_events = lambda objects, query: Event.objects.query(query, objects)
    (events, pages) = filter_objects(Event, list_context, query_objects = query_events, filter_permissions = filter_permissions, get_objects_for_categories = get_events_for_categories, final_filter = add_events_metainfo)
    
    list_context["events"] = events
    list_context["filter_categories"] = {"Past Events" : "past", "Future Events" : "future", "Semester Events" : "semester"}
    list_context["page_range"] = range(1, pages+1)
    
    return render_to_response("event/ajax/list_events.html", list_context, context_instance = RequestContext(request))



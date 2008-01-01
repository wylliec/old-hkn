from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from hkn.list import get_list_context, filter_objects
from hkn.event.models import *
from string import atoi

def list(request, event_category):
    d = get_list_context(request, default_sort = "-start_time", default_category = event_category)    
    d["objects_url"] = "/event/list_ajax"
    d["extra_body"] = get_template("event/ajax/list_javascript.html").render({})
    return render_to_response("list/list.html", d, context_instance=RequestContext(request))


def query_events(objects, query):
    events = objects    
    if query and len(query.strip()) != 0:
        for q in query.split(" "):
            if len(q.strip()) == 0:
                continue
            events = events.filter(Q(name__icontains = q) | Q(location__icontains = q) | Q(description__icontains = q))
    return events

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

def filter_event_permissions(permissions, objects):
    return objects.filter(view_permission__in = permissions)

def list_ajax(request):
    list_context = get_list_context(request, default_sort = "-start_time")
    permissions = request.user.get_all_permissions()
    filter_permissions = lambda x: filter_event_permissions(permissions, x)
    (events, pages) = filter_objects(Event, list_context, query_objects = query_events, filter_permissions = filter_permissions, get_objects_for_categories = get_events_for_categories)
    
    list_context["events"] = events
    list_context["page_range"] = range(1, pages+1)
    
    return render_to_response("event/ajax/list_events.html", list_context, context_instance = RequestContext(request))



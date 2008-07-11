from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers
from ajaxlist import get_list_context, filter_objects
from hkn.event.models import *
from string import atoi


def filter_events_by_category(clazz, objects, category):
    try:
        objects = objects & clazz.__dict__[category].manager.all()
        return objects;
    except:
        pass
    
    category = category.upper()
    if not category in EVENT_TYPE:
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

def add_events_metainfo(user, events):
    """
    This is very inefficient right now because the permissions framework is a little limited. In the future should maybe use manual SQL to do the view_permission filtering::

SELECT e.name, (ct.app_label || "." || p.codename) FROM auth_permission p, event_event e, django_content_type ct  WHERE e.rsvp_permission_id = p.id AND ct.id = p.content_type_id AND (ct.app_label || "." || p.codename) = "main.hkn_everyone" 
    """
    perms = user.get_all_permissions()
    events = list(events)
    for event in events:
        view_permission_code = "%s.%s" % (event.view_permission.content_type.app_label, event.view_permission.codename)
        if view_permission_code not in perms:
            events.remove(event)
            continue
        if event.rsvp_none():
            continue
        rsvp_permission_code = "%s.%s" % (event.rsvp_permission.content_type.app_label, event.rsvp_permission.codename)
        if rsvp_permission_code in perms:
            event.can_rsvp = True
        event.num_rsvps = len(event.rsvp_set.all())
    return events

def get_list_events_context(request, category=None):
    list_context = get_list_context(request, default_sort = "-start_time", default_category = category)
    query_events = lambda objects, query: Event.objects.query(query, objects)
    list_context["list_objects"] = filter_objects(Event, list_context, query_objects = query_events, get_objects_for_categories = get_events_for_categories, final_filter = lambda events: add_events_metainfo(request.user, events))
    list_context["filter_categories"] = {"Past Events" : "past", "Future Events" : "future", "Semester Events" : "semester"}
    list_context["header_template"] = "event/ajax/_list_events_header.html"
    list_context["row_template"] = "event/ajax/_list_events_row.html"
    #list_context["can_edit"] = request.user.has_perm("event.change_event")
    return list_context



def list_events(request, category):
    list_context = get_list_events_context(request, category)
    list_context["objects_url"] = urlresolvers.reverse("hkn.event.list.list_events_ajax")
    list_context["extra_javascript"] = "event/ajax/list_events_javascript.html"
    return render_to_response("ajaxlist/ajaxview.html", list_context, context_instance=RequestContext(request))


def list_events_ajax(request):
    list_context = get_list_events_context(request)
    return render_to_response("ajaxlist/_objects_view.html", list_context, context_instance = RequestContext(request))



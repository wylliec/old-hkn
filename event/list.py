from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers

from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, sort_objects, paginate_objects, render_ajaxlist_response

from hkn.event.models import *
from string import atoi

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
    
def list_events(request, category):
    d = get_ajaxinfo(request.GET)
    d['category'] = category
    if d['sort_by'] == "?":
        d['sort_by'] = "-start_time"
        
    try:
        events = Event.__dict__[category].manager.all()
    except KeyError:
        raise Http404

    if d.has_key('query'):
        events = events.ft_query(d['query'])
    
    events = sort_objects(events, d['sort_by'], None)
    events = paginate_objects(events, d, page=d['page'])
    
    events = add_events_metainfo(request.user, events)
    
    d['events'] = events
    d['can_edit'] = request.user.has_perm('event.change_event')
    
    return render_ajaxlist_response(request.is_ajax(), "event/list.html", d, context_instance=RequestContext(request))

from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers

from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, sort_objects, paginate_objects, render_ajaxlist_response

from hkn.event.models import *
from hkn.event.utils import add_events_metainfo
from string import atoi

def list_events(request, category):
    d = get_ajaxinfo(request.GET)
    d['category'] = category
    if d['sort_by'] == "?":
        d['sort_by'] = "start_time"
        if category.lower() == "past":
            d['sort_by'] = "-start_time"
        
    try:
        events = Event.__dict__[category].manager.all()
    except KeyError:
        raise Http404

    # HACK: change the query != Search Events
    if d.has_key('query') and d['query'] != "Search Events":
        events = events.ft_query(d['query'])
    
    events = events.filter_permissions(request.user)
    events = sort_objects(events, d['sort_by'], None)
    events = paginate_objects(events, d, page=d['page'])
    
    d['events'] = events
    d['can_edit'] = request.user.has_perm('event.change_event')
    
    return render_ajaxlist_response(request.is_ajax(), "event/list.html", d, context_instance=RequestContext(request))

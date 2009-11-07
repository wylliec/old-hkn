from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core import urlresolvers
from django.utils import simplejson

from django.conf import settings

from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, sort_objects, paginate_objects, render_ajaxlist_response
from string import atoi

from request import registry

from request.models import *

def set_metainfos(requests):
    for request in requests:
        request.set_metainfo()
    return requests

def filter_requests(requests):
    def filter_fn(request):
        return registry[request.content_type.model_class()](request)
    return filter(filter_fn, requests)
    
def list_requests(request, category):
    d = get_ajaxinfo(request.GET)
    d['category'] = category
    if d['sort_by'] == "?":
        d['sort_by'] = "submitted"
        
    requests = Request.objects        
    if category == "actives":
        requests = Request.actives
    elif category == "inactives":
        requests = Request.inactives    
        
    requests = requests.for_user(request.user)
    
    if d.has_key('query'):
        requests = requests.ft_query(d['query'])
    
    num_requests = requests.count()

    requests = sort_objects(requests, d['sort_by'], None)

    # TODO: do we still need the 'confirm_object is not None' filter in the following code? And can we push that filter to the database layer (e.g. requests.exclude(confirm_object = None) ) instead of filtering in python? We can also hook the post_delete signal on the confirm object to delete requests with orphaned objects...
    # TODO: we only call 'filter_requests' for the 'actives' category. Is this what we want?
    
    if category == 'actives':
        # TODO: this currently materializes all of the requests from the database to filter them! This is pretty bad & should fix if performance becomes a problem. Hopefully there aren't too many active requests at once
        requests = filter_requests(requests)
        # Requests have already been materialized from earlier filter, so we might as well do this following filter before pagination as well
        requests = filter(lambda r: r.confirm_object is not None, requests)
        requests = paginate_objects(requests, d, page=d['page'])
    else:
        # this will only load e.g. 20 requests from the database. Do this before the next filter so we don't have to materialize all requests from the database
        requests = paginate_objects(requests, d, page=d['page'])

        # this will filter the 20 returned from pagination. If all requests are filtered out, we will have problems! But this should be a rare condition (condition is: the confirm_object e.g. the RSVP object has been deleted) so hopefully this will never happen...
        # TODO: hook the post_delete signal on confirm object to delete requests with orphaned objects instead of having the hack on the line below
        requests = filter(lambda r: r.confirm_object is not None, requests)
    d['requests'] = set_metainfos(requests)
    
    return render_ajaxlist_response(request.is_ajax(), "request/list.html", d, context_instance=RequestContext(request))

def list_requests_confirm_ajax(request):
    r = get_object_or_404(Request, pk=request.REQUEST.get("value", ""))
    
    if request.REQUEST:
        action = request.REQUEST.get("action", "unknown")
        print "Action is: %s" % str(action)
        if action == "add":
            confirmed = True
            active = False
        elif action == "unknown":
            confirmed = False
            active = True
        else:
            confirmed = active = False
        comment = request.POST.get("comment", "")
        r.set_confirm(confirmed, comment, confirmed_by=request.user, save_self=False)
        r.active = active
        r.save()
        
        r = Request.objects.get(pk = r.id)
        
    r.set_metainfo()
    if r.active == True:
        state = "unknown"
    elif r.confirmed == False:
        state = "rejected"
    else:
        state = "accepted"
           
    js = """request_select(%d, "%s"); $("#request_%d_comment").text("%s");""" % (r.id, state, r.id, r.comment)
    
    return HttpResponse(js, mimetype='application/javascript')
    
    
    

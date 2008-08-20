from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core import urlresolvers
from django.utils import simplejson

from django.conf import settings

from ajaxlist import get_list_context, filter_objects
from ajaxlist.helpers import get_ajaxinfo, sort_objects, paginate_objects, render_ajaxlist_response
from string import atoi

from request.models import *

def set_metainfos(requests):
    for request in requests:
        request.set_metainfo()
    return requests
    
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
    
    requests = sort_objects(requests, d['sort_by'], None)
    requests = paginate_objects(requests, d, page=d['page'])

    d['requests'] = set_metainfos(requests)
    
    return render_ajaxlist_response(request.is_ajax(), "request/list.html", d, context_instance=RequestContext(request))

def list_requests_confirm_ajax(request):
    r = get_object_or_404(Request, pk=request.POST.get("value", ""))
    
    if request.POST:
        action = request.POST.get("action", "unknown")
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
    
    
    

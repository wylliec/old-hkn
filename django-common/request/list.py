from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core import urlresolvers
from django.utils import simplejson

from hkn.settings import STATIC_PREFIX

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

    d['requests'] = requests
    
    return render_ajaxlist_response(request.is_ajax(), "request/list.html", d, context_instance=RequestContext(request))

def list_requests_confirm_ajax(request):
    r = get_object_or_404(Request, pk=request.POST.get("value", ""))

    if request.POST:
        action = request.POST.get("action", "unknown")
        confirmed = False
        if action == "add":
            confirmed = True
        comment = request.POST.get("comment", "")
        r.set_confirm(confirmed, comment, confirmed_by=request.user)
        if action == "unknown":
            r.active = True      
        r.save()
        
    
    r.set_metainfo()
    confirm_img = None
    if r.active == True:
        confirm_img = STATIC_PREFIX + "images/site/inactive.png"
    elif r.confirmed == False:
        confirm_img = STATIC_PREFIX + "images/site/error.png"
    else:
        confirm_img = STATIC_PREFIX + "images/site/valid.png"
           
    js = """$("#%s_image").attr("src", "%s");
    $("#%s_comment").text("%s");""" % (str(r.id), confirm_img, str(r.id), r.comment)
    
    return HttpResponse(js, mimetype='application/javascript')
    
    
    

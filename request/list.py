from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core import urlresolvers
from hkn.info.models import *
from hkn.info.utils import *
from hkn.auth.decorators import *
from ajaxlist import get_list_context, filter_objects
from string import atoi
from django.utils import simplejson
from hkn.request.types import METAINFO_FUNCTIONS
from hkn.request.models import *



def add_requests_metainfo(requests):
    for r in requests:
        METAINFO_FUNCTIONS[r.type](r)
    return requests

def get_list_requests_context(request, category = None):
    list_context = get_list_context(request, default_sort = "submitted", default_category = category)
    query_requests = lambda objects, query: Request.objects.query(query, objects)
    filter_permissions = lambda objects: Request.objects.for_user(request.user, objects)
    requests = filter_objects(Request, list_context, query_objects = query_requests, category_map = {"all" : "objects"}, filter_permissions = filter_permissions, final_filter = add_requests_metainfo)
    list_context["requests"] = requests
    list_context["filter_categories"] = {"All Requests" : "all", "Active Requests" : "actives", "Inactive Requests" : "inactives"}
    list_context["view_template"] = "request/ajax/_list_requests.html"

    return list_context

#@permission_required("all.view.basic")
def list_requests(request, category):
    list_context = get_list_requests_context(request, category)
    list_context["objects_url"] = urlresolvers.reverse("hkn.request.list.list_requests_ajax")    
    list_context["extra_javascript"] = "request/ajax/_list_requests_javascript.html"
    return render_to_response("ajaxlist/ajaxview.html", list_context, context_instance=RequestContext(request))

def list_requests_ajax(request):
    list_context = get_list_requests_context(request)
    return render_to_response("request/ajax/_list_requests.html", list_context, context_instance = RequestContext(request))

def list_requests_confirm_ajax(request, request_id):
    try:
        r = Request.objects.get(pk = request_id) 
    except:
        return HttpResponse("No request object with id " + request_id)

    if request.POST:
        confirmed = request.POST.get("confirm", None)
        if confirmed == "true":
            confirmed = True
        elif confirmed == "false":
            confirmed = False
        comment = request.POST.get("comment", "")
        r.set_confirm(confirmed, comment)
        r.save()
    
    METAINFO_FUNCTIONS[r.type](r)
    confirm_img = None
    if r.confirm == "None":
        confirm_img = "/images/site/inactive.png"
    elif r.confirm == False:
        confirm_img = "/images/site/error.png"
    else:
        confirm_img = "/images/site/valid.png"
        
    json = {"request_id" : r.id, "image" : confirm_img, "comment" : r.comment}
    
    return HttpResponse(simplejson.dumps(json), mimetype='application/javascript')
    
    
    

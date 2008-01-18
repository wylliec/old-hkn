# tutoring views
from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from hkn.utils import NiceDict
from hkn.utils import NamedList

# Create your views here.
def signup(request):
    context = NiceDict(defaultValue="")
    context['signup_table_width'] = 600
    context['signup_col_width'] = 100
    context['days'] = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
    context['timeslots'] = ("11a-12", "12-1", "1-2", "2-3", "3-4", "4-5")
    
    context['user'] = request.user
    
    prev = [] #list of rows.  Each row is list of Strings
    for slot in context['timeslots']:
        row = NamedList(name=slot)
        for day in context['days']:
            row.append({"name":day + " " + slot,
                        "value":""}, #TODO replace with previously entered value
                        )
        prev.append(row)
    
    context['prev'] = prev
#    context['debug'] = "prev size is %s, first elem of first row is: %s" % (len(prev), prev[0][0].__repr__())
    
    return render_to_response("tutor/signup.html", context,  context_instance = RequestContext(request))

def submit_signup(request):
    return signup(request)
    #return render_to_response("tutor/signup.html", {},  context_instance = RequestContext(request))
    
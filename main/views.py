from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext

from hkn.event.models import *

def main(request):
    events = Event.objects.order_by('-start_time').filter_permissions(request.user)[:10]
    d = {}
    d['today_events'] = events[:2]
    d['week_events'] = events[2:]
    return render_to_response("main/main.html", d, context_instance=RequestContext(request))

from django.utils import simplejson
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.template.defaultfilters import linebreaks, truncatewords

from hkn.event.models import Event

import datetime

def json_time(date):
    return {"year" : date.year,
            "month" : date.month,
            "day" : date.day,
            "hour" : date.hour,
            "minute" : date.minute}

def feed(request):
    #try:
    start_date = datetime.date(year=int(request.GET['start_year']), month=int(request.GET['start_month']), day=int(request.GET['start_day']))
    end_date = datetime.date(year=int(request.GET['end_year']), month=int(request.GET['end_month']), day=int(request.GET['end_day']))
    
#    except:
#        end_date = datetime.datetime.now()
        #start_date = end_date - datetime.timedelta(days=365)
        #raise Http404

    try:
        max_results = int(request.GET['max_results'])
    except:
        max_results = 500
    events = Event.objects.filter(start_time__gte = start_date, end_time__lte = end_date).order_by("start_time").filter_permissions(request.user)[:max_results]
        
    js_events = [{"id" : e.id,
                  "title" : e.name,
                  "location" : e.location,
                  "description" : linebreaks(truncatewords(e.description, 50)),
                  "start_time" : json_time(e.start_time),
                  "end_time" : json_time(e.end_time),
                  "type" : e.event_type
                  } for e in events]
    
    return HttpResponse(simplejson.dumps(js_events), mimetype="application/javascript")

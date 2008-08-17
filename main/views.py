from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from ajaxwidgets.widgets import JQueryAutoComplete
import datetime

from hkn.event.models import *
from hkn.event.utils import add_events_metainfo
from hkn.tutor.views import get_tutor_miniinfo, get_courses_tutored, get_published_assignments

def main(request):
    d = {}

    events = Event.objects.order_by('-start_time').filter_permissions(request.user)[:4]
    events = add_events_metainfo(request.user, events)
    d['today_events'] = events[:1]
    d['week_events'] = events[1:]
    
    d['day'] = datetime.datetime.now().strftime("%A")
    if d['day'] in ("Saturday", "Sunday"):
        d['day'] = "Monday"
    d["tutoring_title"] = "%s's Tutoring Schedule" % d['day']
    schedule, can_tutor = get_tutor_miniinfo(get_published_assignments(), day=d['day'])
    can_tutor = get_courses_tutored(can_tutor)
    d['schedule'] = schedule
    d['canTutor'] = can_tutor
    
    xfa = JQueryAutoComplete(source=reverse('course-course-autocomplete'))
    d['exam_files_autocomplete']= xfa.render(name="course")
    
    d["lorem"] = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aliquam vel enim at lacus placerat fringilla. Integer lectus. Sed ultricies venenatis eros. Curabitur id sem. Maecenas augue est, imperdiet a, interdum at, tempus a, neque. Vivamus condimentum euismod nibh. Sed ornare malesuada enim. Nulla ligula est, adipiscing posuere, tempor eget, posuere sed, nunc. Nulla condimentum. Integer rutrum iaculis ante. Nam placerat. Ut convallis justo quis elit. Praesent orci tellus, porta id, aliquam sit amet, luctus nec, nisi.

Vestibulum ut leo. Phasellus porta fermentum orci. Suspendisse eget elit sed risus congue rutrum. Cras metus libero, iaculis id, venenatis vitae, lacinia nec, nunc. Pellentesque sagittis rutrum nunc. Integer ultricies tortor ac massa. Nam arcu enim, sodales eu, mattis ut, dapibus sit amet, metus. Mauris malesuada lectus nec ipsum. Praesent vel nisl. Ut fermentum tincidunt massa. Curabitur libero. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nam lacus urna, tincidunt quis, consequat ac, porta a, justo. Nam euismod. Maecenas vitae justo vitae erat accumsan condimentum. Cras nec elit in risus lobortis porttitor. Suspendisse ante. Morbi lacinia dictum lacus. Suspendisse tempus dignissim dui. Aenean facilisis, justo auctor auctor pellentesque, nulla diam posuere lorem, vel vehicula ipsum massa vel eros.

Praesent euismod quam et nulla. Donec vitae urna. In dapibus. Nullam risus. Nam egestas, mi sed bibendum luctus, lorem eros bibendum purus, at adipiscing leo arcu eu augue. Aliquam metus. Fusce et magna nec elit consequat pulvinar. Vestibulum quis libero a mauris vestibulum vulputate. Duis odio turpis, pellentesque a, lobortis non, eleifend et, tellus. Vestibulum ligula justo, bibendum ut, vehicula bibendum, accumsan eget, purus.

Sed vel sapien. Nunc lacus. Mauris aliquet, nisl a venenatis posuere, mi orci viverra augue, ac dapibus turpis eros in metus. In aliquet placerat eros. Sed sed turpis. Vivamus mattis metus sed nibh. Aenean consequat elementum erat. Donec condimentum laoreet felis. Maecenas tincidunt velit nec enim. Vivamus nec mi sit amet risus aliquet ornare. Ut auctor feugiat odio. In scelerisque. Mauris at mi id mauris tristique elementum. Nullam tempus ornare elit. Etiam ac libero. Pellentesque sagittis leo sed diam.

In eget mi. Vivamus risus odio, aliquam sit amet, tincidunt ac, blandit at, urna. Mauris porta. In nulla. Cras vestibulum ultrices lectus. Nulla tristique libero non risus. Nam mollis sapien non elit. Sed orci mi, placerat id, congue ac, cursus non, enim. Etiam risus. Nulla interdum, leo vel tincidunt auctor, felis nibh venenatis nisl, eu ultricies lectus mi vel libero. Proin rutrum felis et est. Quisque interdum nulla ut sapien. Sed tempus posuere mi. Donec interdum fringilla ante. Donec vitae enim. Pellentesque iaculis. Nulla aliquet lacus sagittis lectus. Fusce imperdiet quam bibendum enim. """


    return render_to_response("main/main.html", d, context_instance=RequestContext(request))

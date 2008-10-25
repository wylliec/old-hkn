from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from django.conf import settings

from photologue.models import Gallery
from nice_types.semester import Semester
import nice_types.semester

def main(request):
    context = {}

    semesters = Gallery.objects.all().values_list("semester", flat=True).order_by("-semester").distinct()
    semesters = [Semester(x[-4:]) for x in semesters]
    context['semesters'] = semesters

    return render_to_response('yearbook/main.html', context, context_instance=RequestContext(request))

def semester(request, semester=nice_types.semester.current_semester(), page=1):
    context = {}

    galleries = Gallery.objects.filter(is_public=True).filter(semester=semester)

    SAMPLE_SIZE = ":%s" % getattr(settings, 'GALLERY_SAMPLE_SIZE', 5)

    galleries_per_page = 10

    return object_list(request, queryset=galleries, allow_empty=True, paginate_by=galleries_per_page, page=page, extra_context={'sample_size':SAMPLE_SIZE, 'semester':Semester(semester)})

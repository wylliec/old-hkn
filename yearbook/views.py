from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from photologue.models import Gallery

def main(request):
    context = {}

    context['semesters'] = set(Gallery.objects.all().values_list("semester", flat=True))

    return render_to_response('yearbook/main.html', context, context_instance=RequestContext(request))

from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

def main(request):
	return render_to_response("main/main.html", context_instance=RequestContext(request))

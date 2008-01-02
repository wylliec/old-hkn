from hkn.event.models import *
from hkn.event.forms import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms

def main(request):
	return render_to_response("exam/main.html", context_instance=RequestContext(request))

def faq(request):
	return render_to_response("exam/faq.html", context_instance=RequestContext(request))

def committee(request):
	return render_to_response("exam/committee.html", context_instance=RequestContext(request))

def onlineexams(request):
	return render_to_response("exam/onlineexams.html", context_instance=RequestContext(request))

def submit(request):
	return render_to_response("exam/submit.html", context_instance=RequestContext(request))

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.contrib.auth.decorators import login_required
import datetime

from models import Problem
from form import ProblemForm
from tagging.models import Tag, TaggedItem
import tagging.utils

try: 
	from settings import EXAM_LOGIN_REQUIRED
except:
	EXAM_LOGIN_REQUIRED = True

def search(request):
	if request.GET:
		tags = request.GET['input']
		results = TaggedItem.objects.get_by_model(Problem, tags)
		return render_to_response("review/search.html", {'results' : results}, context_instance=RequestContext(request))
	else:
		return render_to_response("review/search.html", context_instance=RequestContext(request))
	
def browse_review_tags(request):
	tags = Tag.objects.cloud_for_model(Problem, steps=4, distribution=tagging.utils.LINEAR)
	sorted_tags = []
	last_char = None
	for t in tags:
		if last_char == t.name[0]:
			sorted_tags[-1].append(t)
		else:
			last_char = t.name[0]
			sorted_tags.append([t])
		
		
	return render_to_response("review/browse_review_tags.html", {'tags' : sorted_tags}, context_instance=RequestContext(request))
	
def view_tag(request, tag_name = None):
	tag = get_object_or_404(Tag, name = tag_name)
	rel_tags = Tag.objects.related_for_model(tag_name, Problem)
	problems = TaggedItem.objects.get_by_model(Problem, tag) 
	if not problems:
		raise Http404
		
	return render_to_response("review/view_tag.html", {'rel_tags': rel_tags , 'tag':tag_name, 'problems':problems}, context_instance=RequestContext(request))

def view_problem(request, problem_id = None):
	problem = get_object_or_404(Problem, pk = problem_id)
	return render_to_response("review/view_problem.html", {'problem':problem}, context_instance=RequestContext(request))
	
def submit(request):
	if request.method == 'POST':
		form = ProblemForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect("/review/")
	else :
		form = ProblemForm()
		
	return render_to_response("review/submit.html", {'form' : form}, context_instance=RequestContext(request))
	
	

if EXAM_LOGIN_REQUIRED:
    submit = login_required(submit)

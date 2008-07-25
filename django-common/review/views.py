from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from django.contrib.auth.decorators import login_required

import datetime
import sets
import os

from review.models import Problem
from review.form import ProblemForm
from ajaxlist.helpers import sort_objects, paginate_objects, render_ajaxwrapper_response, retrieve_checks
from tagging.models import Tag, TaggedItem
import tagging.utils

try: 
	from settings import EXAM_LOGIN_REQUIRED
except:
	EXAM_LOGIN_REQUIRED = True

def search(request):
	if request.GET:
		tags = lower(request.GET['input'])
		if tags.find(',') == -1:
			tags = r'"' + tags + r'"'
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
	

def view_selected(request):
	problems = []
	if 'selected_problems' in request.session:
		for id in request.session['selected_problems']:
			problems.append(get_object_or_404(Problem, pk=id))
			
	return render_to_response("review/selected.html", {'problems':problems}, context_instance=RequestContext(request))
	
def add_selected(request):
	if request.POST:
		additions = request.POST['problems'].split(' ')
		if 'selected_problems' in request.session:
			for a in additions:
				request.session['selected_problems'].add(a)
		else:
			request.session['selected_problems'] = set(additions)
	else:
		raise Http404

def remove_selected(request):
	if request.POST:
		remove = request.POST['problems'].split(' ')
		if 'selected_problems' in request.session:
			for r in remove:
				request.session['selected_problems'].remove(r)
	else:
		raise Http404

def merge_problems(request, solutions):
	command = "pdftk "
	problems = []
	if 'selected_problems' in request.session:
		for id in request.session['selected_problems']:
			problems.append(get_object_or_404(Problem, pk=id))
	
	for p in problems:
		if not solutions:
			command+= p.get_question_url()[1:] + " "
		else:
			command+= p.get_answer_url()[1:]+ " "
		
	command += "output tmp.pdf"
	
	os.system(command)
	result = file("tmp.pdf", "rb")
	response = HttpResponse(result.read(), mimetype='application/pdf')
	
	if not solutions:
		response['Content-Disposition'] = 'attachment; filename=review_questions.pdf'
	else:
		response['Content-Disposition'] = 'attachment; filename=review_solutions.pdf'
	
	return response

def test(request):
	sort_by = "name"
	p = int(request.POST.get("page", 1))
	
	d = {}
	problems = Problem.objects.all()
	problems = sort_objects(problems, "name")
	problems, d = paginate_objects(problems, d, page=p)
	d['list_objects'] = problems
	d['printinfo'] = request.POST.get("action", "None")
	d['page'] = p
	
	if request.is_ajax():
		return render_ajaxwrapper_response("review/test.html", d, context_instance=RequestContext(request))
	else:
		return render_to_response("review/test.html", d, context_instance=RequestContext(request))
		
if EXAM_LOGIN_REQUIRED:
    submit = login_required(submit)

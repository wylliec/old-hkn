from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet

import datetime
import sets
import os

from review.models import Problem
from review.form import ProblemForm
from ajaxlist.helpers import get_ajaxinfo, sort_objects, paginate_objects, render_ajaxlist_response
from tagging.models import Tag, TaggedItem
import tagging.utils

try: 
	from settings import EXAM_LOGIN_REQUIRED
except:
	EXAM_LOGIN_REQUIRED = True

def search(request):	
	d = get_ajaxinfo(request.GET)
	if d['sort_by'] == "?":
		d['sort_by'] = "name"
	
	tags = get_tag_query(request.GET)
	problems = TaggedItem.objects.get_by_model(Problem, tags)
	problems = sort_objects(problems, d['sort_by'], d['order'])
	problems = paginate_objects(problems, d, page=d['page'])
	d['results'] = problems
	
	return render_ajaxlist_response(request.is_ajax(), "review/search.html", d, context_instance=RequestContext(request))
		
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
	d = get_ajaxinfo(request.GET)
	if d['sort_by'] == "?":
		d['sort_by'] = "name"
		
	tags = tag_name + ", " + get_tag_query(request.GET)
	tag = get_object_or_404(Tag, name = tag_name)
	rel_tags = Tag.objects.related_for_model(r'"' + tag_name + r'"' , Problem)
	problems = TaggedItem.objects.get_by_model(Problem, tags) 
	problems = sort_objects(problems, d['sort_by'], d['order'])
	problems = paginate_objects(problems, d, page=d['page'])
	d['tag'] = tag_name
	d['rel_tags'] = rel_tags
	d['problems'] = problems
	
	return render_ajaxlist_response(request.is_ajax(), "review/view_tag.html", d, context_instance=RequestContext(request))
	
def view_problem(request, problem_id = None):
	problem = get_object_or_404(Problem, pk = problem_id)
	if request.is_ajax():
		rating = request.POST.get("rating", None)
		try:
			rating = int(rating)
		except:
			raise Http404
		
		if rating and rating >= 0 and rating <= 10:
			problem.rate(rating)
			problem.save()
		return render_to_response("review/_bar.html", {'val':problem.difficulty}, context_instance=RequestContext(request))
		
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
	problems = Problem.objects.none()
	if 'ajaxlist_problems' in request.session:
		problems = Problem.objects.filter(pk__in=list(request.session['ajaxlist_problems']))

	tags = get_tag_query(request.GET)
	if tags != "":
		problems = problems & TaggedItem.objects.get_by_model(Problem, tags)
		
	return render_ajaxlist_response(request.is_ajax(), "review/selected.html", {'problems' : problems}, context_instance=RequestContext(request))

def merge_problems(request, solutions):
	command = "pdftk "
	problems = []
	if 'ajaxlist_problems' in request.session:
		for id in request.session['ajaxlist_problems']:
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

# Helpers
def get_tag_query(dict):
	tags = dict.get("query", "")\
	
	tags = tags.lower()
	if tags != "" and tags.find(',') == -1:
		tags = r'"' + tags + r'"'
		
	return tags

if EXAM_LOGIN_REQUIRED:
	submit = login_required(submit)

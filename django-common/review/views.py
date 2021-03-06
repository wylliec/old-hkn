from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse

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
		
	tag = get_object_or_404(Tag, name = tag_name)
	rel_tags = Tag.objects.related_for_model(r'"' + tag_name + r'"' , Problem)
	problems = TaggedItem.objects.get_by_model(Problem, r'"' + tag_name + r'"') 
	problems = sort_objects(problems, d['sort_by'], d['order'])
	problems = paginate_objects(problems, d, page=d['page'])
	d['query'] = tag_name
	d['tag'] = tag_name
	d['rel_tags'] = rel_tags
	d['problems'] = problems
	
	return render_ajaxlist_response(request.is_ajax(), "review/view_tag.html", d, context_instance=RequestContext(request))
	
def view_problem(request, problem_id = None):
	problem = get_object_or_404(Problem, pk = problem_id)
	if "rating" in request.POST:
		rating = request.POST.get("rating", None)
		try:
			rating = int(rating)
		except:
			rating = None
		
		if rating and rating >= 0 and rating <= 10:
			problem.rate(rating)
			problem.save()
	
	if "tag" in request.POST:
		tag = request.POST.get("tag", None)
		tag = tag.lower()
		if tag.find('"') == -1 and tag.find(",") == -1 and tag != "":
			tag = r'"' + tag + r'"'
			problem.add_tag(tag)
			problem.save()
			
	if request.is_ajax():
		return render_to_response("review/_bar.html", {'val':problem.difficulty}, context_instance=RequestContext(request))
	else:
		return render_to_response("review/view_problem.html", {'problem':problem}, context_instance=RequestContext(request))
	
def submit(request):
	if request.method == 'POST':
		form = ProblemForm(request.POST, request.FILES)
		if form.is_valid():
			form.save(commit=False)
			form.submitter = request.user
			form.save()
			return HttpResponseRedirect("/review/")
	else :
		form = ProblemForm()
		
	return render_to_response("review/submit.html", {'form' : form}, context_instance=RequestContext(request))
	
def view_selected(request):
	problems = Problem.objects.none()
	if 'ajaxlist_problems' in request.session:
		problems = Problem.objects.filter(pk__in=request.session['ajaxlist_problems'])
		
	return render_ajaxlist_response(request.is_ajax(), "review/selected.html", {'problems' : problems}, context_instance=RequestContext(request))

def merge_problems(request, solutions):
	command = "pdftk "

	if 'ajaxlist_problems' in request.session and len(request.session['ajaxlist_problems']) > 0:
		problems = Problem.objects.filter(pk__in=request.session['ajaxlist_problems'])
	else:
		return HttpResponseRedirect(reverse("review-selected"))
	
	
	
	for p in problems:
		if not solutions:
			command+= p.question.url[1:] + " "
		else:
			command+= p.answer.url[1:]+ " "
		
	command += "output tmp.pdf"
	
	os.system(command)
	try:
		result = file("tmp.pdf", "rb")
	except:
		raise Http404
		
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

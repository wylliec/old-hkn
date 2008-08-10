from django.http import HttpResponseRedirect, Http404, HttpResponse

def add(request, obj_name, value):
    if obj_name in request.session:
        request.session[obj_name].add(value)
    else:
        request.session[obj_name] = set([value])
    
    return HttpResponse("", mimetype='application/javascript')
    
def remove(request, obj_name, value):
    if obj_name in request.session:
        request.session[obj_name].remove(value)
    
    return HttpResponse("", mimetype='application/javascript')

def clear(request):
	obj_name = request.GET.get("identifier", None)
	if not obj_name:
		raise Http404
	
	obj_name = 'ajaxlist_' + obj_name
	if obj_name in request.session:
		del request.session[obj_name] 
	
	if request.is_ajax():
		return HttpResponse("", mimetype='application/javascript')
	else:
		url = request.GET.get("redirect_to", "/")
		return HttpResponseRedirect(url);

def post(request):
	action = request.POST.get("submit", None)
	obj_name = request.POST.get("identifier", None)
	if not action or not obj_name or obj_name == "none":
		raise Http404
	
	for value in request.POST.getlist("object"):
		if action == "Add":
			add(request, "ajaxlist_%s" % obj_name, value)
		if action == "Remove":
			remove(request, "ajaxlist_%s" % obj_name, value)
			
	
	return HttpResponseRedirect(request.POST.get("redirect_to", "/"))
	

#Called by ajax post requests
def post_ajax(request):
	value = request.POST.get("value", None)
	action = request.POST.get("action", "unknown").lower()
	obj_name = request.POST.get("identifier", None)
	if obj_name == "none" or not value:
		return HttpResponse("");
	if action == "add":
		return add(request, "ajaxlist_%s" % obj_name, value)
	if action == "remove":
		return remove(request, "ajaxlist_%s" % obj_name, value)
		
	return HttpResponse("alert('failed')")    

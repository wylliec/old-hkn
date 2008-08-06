from django.http import HttpResponseRedirect, Http404, HttpResponse

def add(request, obj_name, value):
    if obj_name in request.session:
        request.session[obj_name].add(value)
    else:
        request.session[obj_name] = set([value])
    
    return HttpResponse("alert('success')", mimetype='application/javascript')
    
def remove(request, obj_name, value):
    if obj_name in request.session:
        request.session[obj_name].remove(value)
    
    return HttpResponse("alert('success')", mimetype='application/javascript')

def clear(request, obj_name):
	if obj_name in request.session:
		del request.session[obj_name] 
	
	return HttpResponse("alert('success')", mimetype='application/javascript')
	
#Called by ajax post requests
def post(request):
	value = request.POST.get("value", None)
	action = request.POST.get("action", "unknown").lower()
	obj_name = request.POST.get("identifier", None)
	if obj_name == "none" or not value:
		return HttpResponse("");
	if action == "add":
		return add(request, "ajaxlist_%s" % obj_name, value)
	if action == "remove":
		return remove(request, "ajaxlist_%s" % obj_name, value)
	if action == "clear":
		return clear(request, "ajaxlist_%s" % obj_name)
		
	return HttpResponse("alert('failed')")    

from django.http import HttpResponseRedirect, Http404, HttpResponse

#Called by ajax post requests
def add(request):
	value = request.POST.get("value", None)
	obj_name = request.POST.get("identifier", None)
	if obj_name == "none" or not value:
		return
	
	obj_name = "ajaxlist_" + obj_name
	if obj_name in request.session:
		request.session[obj_name].add(value)
	else:
		request.session[obj_name] = set([value])
	
	return HttpResponse("success")
	
def remove(request):
	value = request.POST.get("value", None)
	obj_name = request.POST.get("identifier", None)
	if obj_name == "none" or not value or not obj_name:
		return
	
	obj_name = "ajaxlist_" + obj_name
	if obj_name in request.session:
		request.session[obj_name].remove(value)
	
	return HttpResponse("success")	

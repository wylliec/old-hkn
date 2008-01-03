from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator, InvalidPage
from hkn.info.models import *
from hkn.info import utils
from hkn.auth.decorators import *
from hkn import semester
from string import atoi

@login_required
#@permission_required("all.view.basic")
def elect(request):
	sem = semester.getNextSemester()

	if request.POST:
		keys = request.POST.keys()
		for k in keys:
			person = Person.objects.get(pk = k)
			committee_name = request.POST[k]
			if committee_name == "delete":
				try:
					Officership.objects.get(person = person, semester = sem).delete()
				except Officership.DoesNotExist:
					pass
				continue

			committee = Position.objects.getPosition(committee_name)
			try:
				os = Officership.objects.get(person = person, semester = sem)
				os.position = committee
			except Officership.DoesNotExist:
				os = Officership(person = person, position = committee, semester = sem)
			os.save()
		
	officerships = Officership.objects.filter(semester = sem).order_by('position')
	
	d = {"officerships" : officerships, "positions" : Position.objects.all()}
	
	return render_to_response("info/elect.html", d, context_instance=RequestContext(request))

def revolt(request):
	return None


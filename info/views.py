from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from hkn.info.models import *
from hkn.info.forms import ChangePictureForm, profile_form_for_person

@login_required
def profile(request):
    if request.POST:
        form = profile_form_for_person(request.user.person, request.POST)
        if form.is_valid():
            form.save_for_person()
            request.user.message_set.create(message="Profile updated successfully")
            form = profile_form_for_person(request.user.person)
        else:
            data = form.data.copy()
            for field in ('current_password', 'new_password', 'confirm_new_password'):
                if data.has_key(field):
                    del data[field]
            form.data = data
    else:
        form = profile_form_for_person(request.user.person)
    
    return render_to_response("info/profile.html", {'form' : form, 'person' : request.user.person}, context_instance=RequestContext(request))


@login_required
def change_picture(request):
    if request.method == "POST":
        form = ChangePictureForm(request.POST, request.FILES)
        if form.is_valid():
            form.save_for_person(request.user.person)
            request.user.message_set.create(message="Picture updated successfully")
            return HttpResponseRedirect(reverse("info-person-profile"))
    else:
        form = ChangePictureForm()
        
    return render_to_response("info/change_picture.html", {'form' : form, 'person' : request.user.person}, context_instance=RequestContext(request))
    

def person_autocomplete(request, member_type):
    def iter_results(people):
        if people:
            for r in people:
                yield '%s|%s\n' % (r.name, r.id)
    
    if not request.GET.get('q'):
        return HttpResponse(mimetype='text/plain')
    
    q = request.GET.get('q')
    limit = request.GET.get('limit', 15)
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest() 

    if (member_type == 'all_officers')
        people = Person.all_officers.ft_query(q)[:limit]
    return HttpResponse(iter_results(people), mimetype='text/plain')


from django.http import *
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from hkn import auth
from hkn.auth.models import *
from hkn.info.models import *
from hkn.auth.utils import REDIRECT_FIELD_NAME, PERSONID_KEY
from hkn.auth import utils

# Create your views here.

DEFAULT_REDIRECT_URL = "/hkn/list"

def login(request, redirect_url = None, message = ""):
	if redirect_url is None:
		redirect_url = request.REQUEST.get(REDIRECT_FIELD_NAME, DEFAULT_REDIRECT_URL)

	d = { "redirect_url" : redirect_url, "message" : message }
	return render_to_response("auth/login.html", d)

def logout(request):
	utils.logout(request)
	return HttpResponse("Logged out!")

def authenticate(request):
	username = request.POST.get("username")
	password = request.POST.get("password")
	redirect_url = request.POST.get("redirect_url")
	account = None
	try:
		account = User.objects.get(username = username)
	except User.DoesNotExist:
		return login(request, redirect_url, message="Account does not exist!")
	
	if not account.checkPassword(password):
		return login(request, redirect_url, message="Password incorrect!")

	utils.login(request, account)
	#request.session[PERSONID_KEY] = account.person_id

	#if account.force_password_change:
	#	return change_password(request, redirect_url)
	#if account.force_info_update:
#		return info_update(request, redirect_url)

	return HttpResponseRedirect(redirect_url)
	#return HttpResponse("Authenticated!")

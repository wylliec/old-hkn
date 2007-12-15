from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# Example:
	# (r'^candportal/', include('candportal.foo.urls')),
	
	# View URL patterns go here:
		(r'$', 'hkn.auth.login.login'),
	)
					    

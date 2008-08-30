from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    url(r'^infosession/register/$', 'hkn.indrel.views.infosession_registration', name='indrel-infosession-registration'),
    url(r'^infosession/register/complete/$', 'hkn.indrel.views.infosession_registration_complete', name='indrel-infosession-registration-complete'),
    )					    

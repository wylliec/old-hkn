from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    url(r'^infosession/register/$', 'hkn.indrel.views.infosession_registration', name='indrel-infosession-registration'),
    url(r'^infosession/register/complete/$', 'hkn.indrel.views.infosession_registration_complete', name='indrel-infosession-registration-complete'),
    url(r'^resume-book/register/$', 'hkn.indrel.views.resume_book_registration', name='indrel-resume-book-registration'),
    url(r'^resume-book/register/complete/$', 'hkn.indrel.views.resume_book_registration_complete', name='indrel-resume-book-registration-complete'),
    )					    

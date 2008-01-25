from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # View URL patterns go here:
        #(r'^$', 'hkn.info.list.list_all'),
        (r'^find_course/$', 'hkn.course.course.find_course'),      

        #(r'^?P<committee>\w/$', 'hkn.info.list.list_committee'),
    )                        

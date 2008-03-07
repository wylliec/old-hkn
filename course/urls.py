from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # View URL patterns go here:
        #(r'^$', 'hkn.info.list.list_all'),
        (r'^find_course/$', 'hkn.course.course.find_course'),      
        (r'^course_autocomplete/$', 'hkn.course.course.course_autocomplete'),              
        (r'^instructor_autocomplete/$', 'hkn.course.instructor.instructor_autocomplete'),                      

        #(r'^?P<committee>\w/$', 'hkn.info.list.list_committee'),
    )                        

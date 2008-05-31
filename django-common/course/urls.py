from django.conf.urls.defaults import *

urlpatterns = patterns('',
        (r'^find_course/$', 'course.course.find_course'),      
        (r'^course_autocomplete/$', 'course.course.course_autocomplete'),              
        (r'^instructor_autocomplete/$', 'course.instructor.instructor_autocomplete'),                      
    )                        

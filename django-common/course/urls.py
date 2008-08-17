from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^find_course/$', 'course.views.find_course', name="course-find-course"),
        url(r'^course_autocomplete/$', 'course.views.course_autocomplete', name="course-course-autocomplete"),              
        url(r'^instructor_autocomplete/$', 'course.instructor.instructor_autocomplete', name="course-instructor-autocomplete"), 
    )                        

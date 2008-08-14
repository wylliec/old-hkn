from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^candportal/', include('candportal.foo.urls')),
    

    # View URL patterns go here:
        #(r'^$', 'hkn.info.list.list_all'),
        url(r'^view/(?P<person_id>\w+)/$', 'hkn.info.person.view', name="person-view"),
        url(r'^change-profile/', 'hkn.info.views.profile', name='info-person-profile'),
        url(r'^change-photo/', 'hkn.info.views.change_picture', name='info-person-change-picture'),        
        url(r'^thumbnail/(?P<person_id>\d+)/$', 'hkn.info.person.pictures', name="person-thumbnail"),

        url(r'^list/(?P<category>.*)/$', 'hkn.info.list.list_people', name="person-list-category"),
        url(r'^list/$', 'hkn.info.list.list_people', {"category" : "all"}, name="person-list-all"),
        #url(r'^list_people_ajax/$', 'hkn.info.list.list_people_ajax', name="person-list-ajax"),
        url(r'^quiz/(?P<category>.*)/$', 'hkn.info.quiz.quiz', "person-quiz-category"),

        url(r'^find_person/$', 'hkn.info.find.find_person'),
        url(r'^elect/$', 'hkn.info.elect.elect'),
        url(r'^revolt/$', 'hkn.info.elect.revolt'),		


        url(r'^tutor-infobox/(?P<person_id>\d+)/$', 'hkn.info.infobox.tutor', name="person-tutor-infobox"), 
    )					    

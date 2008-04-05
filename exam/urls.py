from django.conf.urls.defaults import *
from hkn.settings import SERVER_ROOT, IMAGES_PATH

urlpatterns = patterns('',
    # Example:

    # main page
    (r'^$', 'hkn.exam.views.main'),
    (r'^faq/$', 'hkn.exam.views.faq'),
    (r'^committee/$', 'hkn.exam.views.committee'),
    (r'^onlineexams/$', 'hkn.exam.views.onlineexams'),
    (r'^submit/$', 'hkn.exam.exam.submit'),
    (r'^browse/(?P<department_abbr>.*)/$', 'hkn.exam.views.browse_department'),
    (r'^browse/$', 'hkn.exam.views.browse'),
    (r'^list/(?P<course>.*)/(?P<exam_type>.*)/$', 'hkn.exam.list.list_exams'),    
    (r'^list/(?P<course>.*)/$', 'hkn.exam.list.list_exams'),
    (r'^list/$', 'hkn.exam.list.list_exams'),
    (r'^list_ajax/$', 'hkn.exam.list.list_exams_ajax'),        
)

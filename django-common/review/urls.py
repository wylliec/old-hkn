from django.conf.urls.defaults import *
from settings import SERVER_ROOT

urlpatterns = patterns('',
    (r'^$', 'review.views.search'),
    (r'^submit/$', 'review.views.submit'),
    (r'^tag/(?P<tag_name>.*)/$', 'review.views.view_tag'),
    (r'^problem/(?P<problem_id>.*)/$', 'review.views.view_problem'),
    (r'^browse/$', 'review.views.browse_review_tags'),  
    (r'^search$', 'review.views.search'),
    (r'^search?input=', 'review.views.search'),
)

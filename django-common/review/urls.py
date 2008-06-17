from django.conf.urls.defaults import *
from settings import SERVER_ROOT

urlpatterns = patterns('',
    url(r'^$', 'review.views.search', name='review-home'),
    url(r'^submit/$', 'review.views.submit', name='review-submit'),
    url(r'^tag/(?P<tag_name>.*)/$', 'review.views.view_tag', name='review-tag'),
    url(r'^problem/(?P<problem_id>.*)/$', 'review.views.view_problem', name='review-problem'),
    url(r'^browse/$', 'review.views.browse_review_tags', name='review-browse-tags'),  
    url(r'^search$', 'review.views.search', name='review-search'),
)

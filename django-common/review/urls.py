from django.conf.urls.defaults import *
from settings import SERVER_ROOT

urlpatterns = patterns('',
    url(r'^$', 'review.views.search', name='review-home'),
    url(r'^submit/$', 'review.views.submit', name='review-submit'),
    url(r'^tag/(?P<tag_name>.*)/$', 'review.views.view_tag', name='review-tag'),
    url(r'^problem/(?P<problem_id>.*)/$', 'review.views.view_problem', name='review-problem'),
    url(r'^browse/$', 'review.views.browse_review_tags', name='review-browse-tags'),  
    url(r'^search$', 'review.views.search', name='review-search'),
    url(r'^selected/$', 'review.views.view_selected', name='review-selected'),
    url(r'^selected/add/$', 'review.views.add_selected', name='review-add-selected'), 
    url(r'^selected/remove/$', 'review.views.remove_selected', name='review-remove-selected'), 
    url(r'^selected/merge/problems$', 'review.views.merge_problems', name='review-merge-problems'),
    url(r'^selected/merge/solutions$', 'review.views.merge_solutions', name='review-merge-solutions'),
)

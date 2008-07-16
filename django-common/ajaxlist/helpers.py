# file template.py

import new
from django.template.loader_tags import BlockNode, ExtendsNode
from django.template import loader, Context, RequestContext, TextNode
from django.templatetags.ajaxtable import AjaxWrapperNode
from django.core.paginator import Paginator
from django.http import HttpResponse

class NodeNotFound(Exception):
    pass

def get_node(nodelist, node):
	for n in nodelist:
		if isinstance(n, node):
			return n
		try:
			ret = get_node(n.nodelist, node)
			if ret:
				return ret
		except:
			pass
		
	return None
    
####################
# Ajaxlist View helpers
####################
    
def render_ajaxwrapper_response(template, dictionary, context_instance=None, mimetype=None):
	""" Returns an HttpResponse object with the contents in the ajaxwrapper tag of the template"""
	t = loader.get_template(template)
	dictionary = dictionary or {}
	if context_instance:
		context_instance.update(dictionary)
	else:
		context_instance = Context(dictionary)
		
	return HttpResponse(render_ajaxwrapper(t, context_instance), mimetype=mimetype)

def render_ajaxwrapper(template, context):
	b = get_node(template.nodelist, AjaxWrapperNode)
	if b:
		return b.render_inside(context)
	else:
		raise NodeNotFound

def sort_objects(objects, field_name):   
	""" Sort objects by a field name """
	return objects.order_by(field_name)

def paginate_objects(objects, list_context, page=1, max_per_page=20):
	"""
	Breaks objects into pages and adds page info to the context
	
	Returns the objects on the page specified and the context
	"""
	paginator = Paginator(objects, max_per_page)
	p = paginator.page(page) 
	
	list_context["has_next_page"] = p.has_next()
	list_context["has_previous_page"] = p.has_previous()
	list_context["page_range"] = paginator.page_range

	return p.object_list, list_context
	
	
"""

from django.template.context import Context
from ajaxlist.helpers import get_node
from ajaxlist.helpers import render_ajaxwrapper_response
from ajaxlist.helpers import render_ajaxwrapper

from django.templatetags.ajaxtable import AjaxWrapperNode
from django.template.loader import get_template
t = get_template("review/test.html")
isinstance(t.nodelist[0].nodelist[-1].nodelist[-2], AjaxWrapperNode)
"""
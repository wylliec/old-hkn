from django.template.loader import get_template
from django.template import VariableNode, NodeList, TextNode, Variable
from django.template.loader_tags import IncludeNode
from django import template

register = template.Library()

control_templates = { 	
					"search" : "ajaxlist/controls/query2.html", 
					"pager" : "ajaxlist/controls/pager2.html",
					"per_page" : "ajaxlist/controls/per_page2.html",
				}

table_defaults = 	{
					"checks" : "off",
				}
			

class AjaxTableNode(template.Node):
	def __init__(self, objects, header_template, row_template, options):
		self.objects = Variable(objects)
		self.header_template = header_template
		self.row_template = row_template
		for k in table_defaults:
			if not options.get(k, None):
				options[k] = table_defaults[k]
		self.options = options
	
	def __repr__(self):
		return "<AjaxTableNode>"
	
	def render(self, context):
		context.update(self.options)
		context['list_objects'] = self.objects.resolve(context)
		context['header_template'] = self.header_template
		context['row_template'] = self.row_template
		t = get_template("ajaxlist/_objects_list.html")
		return  t.render(context)
		
class AjaxJSNode(template.Node):
	def __init__(self):
		self.js_path = "/static/js/ajaxlist.js"
		
	def __repr__(self):
		return "<AjaxJSNode: %s>" % self.js_path

	def render(self, context):
		return '<script type="text/javascript" src="%s" ></script>' % self.js_path
		
class AjaxControlNode(template.Node):
	def __init__(self, type):
		self.type = type
		
	def __repr__(self):
		return "<AjaxControlNode: %s>" % type
	
	def render(self, context):
		t = get_template(control_templates[self.type])
		return t.render(context)
	
class AjaxWrapperNode(template.Node):
	def __init__(self, nodelist):
		nodelist.insert(0, TextNode('<div id="ajaxwrapper">'))
		nodelist.append(TextNode("</div>"))
		self.nodelist = nodelist
		
	def __repr__(self):
		return "<AjaxWrapperNode>"
	
	def render(self, context):
		return self.nodelist.render(context)
		
	def render_inside(self, context):
		return NodeList(self.nodelist[1:-1]).render(context)

class SpecialForNode(template.defaulttags.ForNode):
	"""
	Same as the For node except it will extract which variable the inner nodes require.
	
	It will use the first variable it finds.
	"""
	def __init__(self, sequence, is_reversed, nodelist_loop):
		self.sequence = sequence
		self.is_reversed = is_reversed
		self.nodelist_loop = nodelist_loop
	
	def __repr__(self):
		return "<Special ForNode: >"
		
	def render(self, context):
		nodelist = NodeList()
		if 'forloop' in context:
			parentloop = context['forloop']
		else:
			parentloop = {}
		context.push()
		try:
			values = self.sequence.resolve(context, True)
		except VariableDoesNotExist:
			values = []
		if values is None:
			values = []
		if not hasattr(values, '__len__'):
			values = list(values)
		len_values = len(values)
		if self.is_reversed:
			values = reversed(values)

		# Create a forloop value in the context.  We'll update counters on each
		# iteration just below.
	
		loop_var = row_variable(self.nodelist_loop, context)

		loop_dict = context['forloop'] = {'parentloop': parentloop}
		for i, item in enumerate(values):
			# Shortcuts for current loop iteration number.
			loop_dict['counter0'] = i
			loop_dict['counter'] = i+1
			# Reverse counter iteration numbers.
			loop_dict['revcounter'] = len_values - i
			loop_dict['revcounter0'] = len_values - i - 1
			# Boolean values designating first and last times through loop.
			loop_dict['first'] = (i == 0)
			loop_dict['last'] = (i == len_values - 1)
			context['object'] = item
			context[loop_var] = item
			
			for node in self.nodelist_loop:
				nodelist.append(node.render(context))
		
		return nodelist.render(context)

@register.tag(name="ajaxtable")
def do_ajaxtable(parser, token):
	bits = token.split_contents()
	if len(bits) < 4:
		raise TemplateSyntaxError("'ajaxtable' should have at least 3 arguments")
	
	objects = bits[1] 
	
	#remove double quotes
	header = bits[2][1:-1] 
	row = bits[3][1:-1]

	options = {}
	try:
		for o in bits[4:]:
			k, v = o.split('=')
			options[k] = v
	except:
		raise TemplateSyntaxError("AjaxTable options have the format [key]=[value]")
		
	return AjaxTableNode(objects, header, row, options)
	
@register.tag(name="special_for")
def do_special_for(parser, token):
	bits = token.contents.split()
	if len(bits) < 2:
		raise TemplateSyntaxError("'for' statements should have at least two"
			" words: %s" % token.contents)
	
	is_reversed = bits[-1] == 'reversed'
	sequence = parser.compile_filter(bits[1])
	nodelist_loop = parser.parse(('endfor',))
	parser.delete_first_token()
	return SpecialForNode(sequence, is_reversed, nodelist_loop)

@register.tag(name="ajaxwrapper")
def do_ajaxwrapper(parser, token):
	nodelist = parser.parse(("endajaxwrapper",))
	parser.delete_first_token()
	return AjaxWrapperNode(nodelist)

@register.tag(name="control")
def do_control(parser, token):
	bits = token.split_contents()
	if len(bits) != 2 :
		raise TemplateSyntaxError("'control' should have one argument")
			
	type = bits[1]
	return AjaxControlNode(type)

@register.tag(name="ajaxlist_js")
def do_ajaxlist_js(parser, token):
	return AjaxJSNode()
	
# Helpers
def row_variable(nodelist, context):
	
	for node in nodelist:
		if isinstance(node, IncludeNode):
			print node.template_name
			print node.template_name.resolve(context)
			print get_template(node.template_name.resolve(context))
			return row_variable(get_template(node.template_name.resolve(context)).nodelist, context)
		if isinstance(node, VariableNode):
			return node.filter_expression.var.__str__().split(".")[0]
	
	return "object"
	

"""
from django.template.loader import get_template
from django.template.context import Context
from ajaxlist.templatetags.ajaxtable import row_variable
c = Context({"header_template" : "review/_problem.html"})
t = get_template("ajaxlist/_objects_list.html")
row_variable(t.nodelist[2:], c)
"""


		
	
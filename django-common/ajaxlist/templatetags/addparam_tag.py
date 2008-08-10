#Example usage in html template:
# <a href="{% addurlparameter sort 1 %}">Sort on field 1</a>
# <a href="{% addurlparameter output pdf %}">Export as pdf</a>

from django.template import Library, Node, resolve_variable, TemplateSyntaxError

register = Library()

class AddParameter(Node):
	def __init__(self, var_pairs):
		self.var_pairs = var_pairs

	def render(self, context):
		req = resolve_variable('request',context)
		params = req.GET.copy()
		var_pairs = self.var_pairs
		while len(var_pairs):
			try:
				params[var_pairs[0]] = resolve_variable(var_pairs[1], context)
			except:
				params[var_pairs[0]] = var_pairs[1]
			var_pairs = var_pairs[2:]
	
		return '%s?%s' % (req.path, params.urlencode())

def addurlparameter(parser, token):
	from re import split
	bits = split(r'\s+', token.contents, 2)
	if len(bits) < 2:
		raise TemplateSyntaxError, "'%s' tag requires at least arguments" % bits[0]
	if len(bits[1:]) % 2:
		raise TemplateSyntaxError, "'%s' tag requires an even number of arguments" % bits[0]
	
	return AddParameter(bits[1:])

register.tag('addurlparameter', addurlparameter)

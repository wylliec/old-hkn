#Example usage in html template:
# <a href="{% addurlparameter sort 1 %}">Sort on field 1</a>
# <a href="{% addurlparameter output pdf %}">Export as pdf</a>

from django.template import Library, Node, resolve_variable, TemplateSyntaxError

register = Library()

class AddParameter(Node):
  def __init__(self, varname, value):
    self.varname = varname
    self.value = value

  def render(self, context):
    req = resolve_variable('request',context)
    params = req.GET.copy()
    try:
      value = resolve_variable(self.value, context)
    except:
      value = self.value
    
    params[self.varname] = value
    return '%s?%s' % (req.path, params.urlencode())

def addurlparameter(parser, token):
  from re import split
  bits = split(r'\s+', token.contents, 2)
  if len(bits) < 2:
    raise TemplateSyntaxError, "'%s' tag requires two arguments" % bits[0]
  return AddParameter(bits[1],bits[2])

register.tag('addurlparameter', addurlparameter)

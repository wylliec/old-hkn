from django import template
from django.template import Node, NodeList, Template, Context, resolve_variable
from django.template import TemplateSyntaxError, VariableDoesNotExist, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END
from django.template import Template
from django.conf import settings


register = template.Library()

def last(value):
    return value[-1]

def render_in_context(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise TemplateSyntaxError, "%r takes 1 argument" % bits[0]
    return RenderInContextNode(bits[1])
render_in_context = register.tag(render_in_context)

class RenderInContextNode(Node):
    def __init__(self, to_render):
        self.to_render = to_render

    def render(self, context):
        to_render_text = resolve_variable(self.to_render, context)
        rendered = Template(to_render_text).render(context)
        context[self.to_render] = rendered
        return ''

def do_ifin(parser, token, negate):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfInNode(bits[1], bits[2], nodelist_true, nodelist_false, negate)


class IfInNode(Node):
    def __init__(self, var1, var2, nodelist_true, nodelist_false, negate):
        self.var1, self.var2 = var1, var2
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfInNode>"

    def render(self, context):
        try:
            val1 = resolve_variable(self.var1, context)
        except VariableDoesNotExist:
            val1 = None
        try:
            val2 = resolve_variable(self.var2, context)
        except VariableDoesNotExist:
            val2 = None
        if (self.negate and val1 not in val2) or (not self.negate and val1 in val2):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


def ifin(parser, token):
    """
    """
    return do_ifin(parser, token, False)
ifin = register.tag(ifin)

def ifnotin(parser, token):
    """
    """
    return do_ifin(parser, token, True)
ifin = register.tag(ifin)
    

register.filter(last)
#register.filter("last", last_val)

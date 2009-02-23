from django.template import Library, Node
     
register = Library()

class SplitListNode(Node):
    def __init__(self, list, cols, new_list):
        self.list, self.cols, self.new_list = list, cols, new_list

    def split_seq(self, list, cols=2):
        start = 0 
        for i in xrange(cols): 
            stop = start + len(list[i::cols]) 
            yield list[start:stop] 
            start = stop

    def render(self, context):
        context[self.new_list] = self.split_seq(context[self.list], int(self.cols))
        return ''

def list_to_columns(parser, token):
    """Parse template tag: {% list_to_colums list as new_list 2 %}"""
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "list_to_columns list as new_list 2"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "second argument to the list_to_columns tag must be 'as'"
    return SplitListNode(bits[1], bits[4], bits[3])
    
list_to_columns = register.tag(list_to_columns)


import copy

from django import template
from django import forms
from django.utils.datastructures import SortedDict

def get_fieldset(parser, token):
    try:
        name, fields, as_, variable_name, from_, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])

    return FieldSetNode(fields.split(','), variable_name, form)

get_fieldset = register.tag(get_fieldset)


class FieldSetNode(template.Node):
    def __init__(self, fields, variable_name, form_variable):
        self.fields = fields
        self.variable_name = variable_name
        self.form_variable = form_variable

    def render(self, context):
        
        form = template.Variable(self.form_variable).resolve(context)
        new_form = copy.copy(form)        
        new_form.fields = SortedDict([(key, value) for key, value in form.fields.items() if key in self.fields])

        context[self.variable_name] = new_form

        return u''


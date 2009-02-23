import copy

from django import template
from django import forms
from django.utils.datastructures import SortedDict

register = template.Library()

def get_fieldsets(parser, token):
    '''
    {% get_fieldsets from form as fieldsets %}
    '''
    try:
        name, from_, form, as_, variable_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])

    return FieldSetsNode(variable_name, form)

get_fieldsets = register.tag(get_fieldsets)

def get_fieldset(parser, token):
    '''
    {% get_fieldset first_name, last_name as name_form from form %}
    '''
    try:
        name, fields, as_, variable_name, from_, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])

    return FieldSetNode(fields.split(','), variable_name, form)

get_fieldset = register.tag(get_fieldset)


class FieldSetsNode(template.Node):
    def __init__(self, variable_name, form_variable):
        self.variable_name = variable_name
        self.form_variable = form_variable

    def render(self, context):
        form = template.Variable(self.form_variable).resolve(context)
        fieldsets = []
        for name, field_names in form.fieldsets:
            new_form = copy.copy(form)
            new_form.fields = SortedDict([(field_name, form.fields[field_name]) for field_name in field_names])
            new_form.help_text = form.fieldset_help.get(name, None)
            fieldsets.append((name, new_form))
        
            
        context[self.variable_name] = fieldsets
        return u''

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


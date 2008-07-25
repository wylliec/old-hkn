# widgets.py

from django import forms
from django.forms.widgets import flatatt, Widget
from django.forms.util import smart_unicode
from django.utils.html import escape
from django.utils.simplejson import JSONEncoder

class JQueryAutoComplete(forms.TextInput):
    def __init__(self, source, options={}, attrs={}):
        """source can be a list containing the autocomplete values or a
        string containing the url used for the XHR request.
        
        For available options see the autocomplete sample page::
        http://jquery.bassistance.de/autocomplete/"""
        
        self.options = None
        self.attrs = {'autocomplete': 'off'}
        self.source = source
        if len(options) > 0 and type(options) == type({}):
            self.options = JSONEncoder().encode(options)
        elif type(options) == type(''):
            self.options = options
        
        self.attrs.update(attrs)
    
    def render_js(self, field_id):
        if isinstance(self.source, list):
            source = JSONEncoder().encode(self.source)
        elif isinstance(self.source, str):
            source = "'%s'" % escape(self.source)
        else:
            raise ValueError('source type is not valid')
        
        options = ''
        if self.options:
            options += ',%s' % self.options

        return u'$(\'#%s\').autocomplete(%s%s);' % (field_id, source, options)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(smart_unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name    
        
        return u'''<input type="text" %(attrs)s/>
        <script type="text/javascript">%(js)s</script>
        ''' % {
            'attrs' : flatatt(final_attrs),
            'js' : self.render_js(final_attrs['id']),
        }

class ModelAutocomplete(Widget):

    autocomplete_field = "%s_auto"    
    hidden_id_field = "%s_id"
    
    def __init__(self, source, attrs={}):
        """source can be a list containing the autocomplete values or a
        string containing the url used for the XHR request.
        
        For available options see the autocomplete sample page::
        http://jquery.bassistance.de/autocomplete/"""
        
        self.options = []
        self.attrs = {'autocomplete': 'off'}
        self.source = source
        
        self.attrs.update(attrs)
        

    def get_options(self):
        return """{formatResult : function(row, text) {
            $("#%(hidden_id_field_id)s").attr("value", row[1]);
            return text;
        } } """
        
    def render_hidden_id_field(self, name):
        return u'''<input type="hidden" id="id_%s" name="%s">''' % (ModelAutocomplete.hidden_id_field % name, ModelAutocomplete.hidden_id_field % name)

    def render_result_javascript(self, name):
        return """<script language="javascript">
            $('input#id_%s').result(function(event, data, formatted) {
                $("input#id_%s").attr("value", data[1]);
            })</script>""" % (ModelAutocomplete.autocomplete_field % name, ModelAutocomplete.hidden_id_field % name)

    def render(self, name, value=None, attrs=None):
        try:
            obj_txt, obj_id = value.split("|")
        except (AttributeError, TypeError, ValueError):
            obj_txt = obj_id = None
        
        #self.options = self.get_options() % { "hidden_id_field_id" : "id_" + ModelAutocomplete.hidden_id_field % name }
        
        output = []
        
        autocomplete_box = JQueryAutoComplete(self.source, self.options, self.attrs)
        autocomplete_html = autocomplete_box.render(ModelAutocomplete.autocomplete_field % name, obj_txt)
        output.append(autocomplete_html)
        
        output.append(self.render_hidden_id_field(name))
        output.append(self.render_result_javascript(name))
        
        return '\n'.join(output)
    
    def value_from_datadict(self, data, files, name):
        obj_txt = data.get(ModelAutocomplete.autocomplete_field % name)
        obj_id = data.get(ModelAutocomplete.hidden_id_field % name)    
        return obj_txt + "|" + obj_id


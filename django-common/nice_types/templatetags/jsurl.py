from django.template import TemplateSyntaxError, VariableDoesNotExist, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END
from django.template import get_library, Library, InvalidTemplateLibrary, Node
from django.utils.datastructures import SortedDict

register = Library()

class JSURLNode(Node):
    def __init__(self, view_name, args, kwargs, asvar, placeholders):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar
        self.placeholders = placeholders

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) if not isinstance(arg, unicode) else arg for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context) if not isinstance(v, unicode) else v)
                       for k, v in self.kwargs.items()])


        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail, 
        # re-raise the NoReverseMatch unless we're using the 
        # {% url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = reverse(self.view_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            project_name = settings.SETTINGS_MODULE.split('.')[0]
            try:
                url = reverse(project_name + '.' + self.view_name,
                              args=args, kwargs=kwargs)
            except NoReverseMatch:
                if self.asvar is None:
                    raise

        url = "'%s'" % url
        for placeholder, jsobj in self.placeholders.items():
            url = ("' + %s + '" % jsobj).join(url.split(placeholder,1))

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

def jsurl(parser, token):
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None
    placeholders = SortedDict()

    def handle_js_value(value):
        if not value.startswith("js:"):
            return parser.compile_filter(value)
        js, jsobj, placeholder = value.split(":")
        placeholders[placeholder] = jsobj
        return unicode(placeholder)

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = handle_js_value(v)
                    elif arg:
                        args.append(handle_js_value(arg))
    return JSURLNode(viewname, args, kwargs, asvar, placeholders)
jsurl = register.tag(jsurl)


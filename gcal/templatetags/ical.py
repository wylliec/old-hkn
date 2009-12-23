from django import template
register = template.Library()

@register.filter
def icaldate(d):
    return d.strftime("%Y%m%dT%H%M%S")

@register.filter
def icalify(string, args):
    st = int(args)
    string = list(string.replace('\r\n', "\\n").replace('\n', '\\n'))
    for i in xrange(74-st, len(string), 74):
        string.insert(i, '\n ')
    return "".join(string)

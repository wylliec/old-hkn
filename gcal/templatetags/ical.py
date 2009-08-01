from django import template
import pytz
register = template.Library()

@register.filter
def icaldate(d):
    try:
        loc_d = pytz.utc.localize(d)
    except pytz.InvalidTimeError:
        loc_d = pytz.utc.localize(d, is_dst=True)
    return d.strftime("%Y%m%dT%H%M%SZ")

@register.filter
def icalify(string, args):
    st = int(args)
    string = list(string.replace('\r\n', "\\n").replace('\n', '\\n'))
    for i in xrange(74-st, len(string), 74):
        string.insert(i, '\n ')
    return "".join(string)

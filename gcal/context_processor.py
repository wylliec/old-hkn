from hkn.gcal.constants import GCAL
from hkn.gcal.utils import getCalendarEntry

try:
    from hkn.hknsettings import GCAL_ENABLE
except:
    GCAL_ENABLE = False


def gcal(request):
   return {"gcal" : GcalQuery()}



class GcalQuery(object):
   def query_string(self):
    if not GCAL_ENABLE:
        return ""
    s = ""
    for etype in GCAL.calendar_titles.keys():
        c = getCalendarEntry(etype)
        cal_id = c.id.text.split("/")[-1]
        cal_color = GCAL.calendar_colors[etype]
        if cal_color[0] == '#':
            cal_color = "%23" + cal_color[1:]
        else:
            cal_color = "%23" + cal_color
        s = "%s&amp;src=%s&amp;color=%s" % (s, cal_id, cal_color)
    return s


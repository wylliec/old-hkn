from hkn.event.constants import EVENT_TYPE
from hkn.constants import _const

GCAL = _const()

GCAL.email = "hkn@mu.etakappanu.net"
GCAL.password = "monkey13"
GCAL.source = "Google_Calendar_HKN_Sync"

GCAL.calendar_titles = {
EVENT_TYPE.CANDMAND : "HKN Candidate Mandatory Events", 
EVENT_TYPE.FUN : "HKN Fun Events",
EVENT_TYPE.BIGFUN : "HKN Big Fun Events",
EVENT_TYPE.COMSERV : "HKN Community Service Events",
EVENT_TYPE.DEPSERV : "HKN Departmental Service Events",
EVENT_TYPE.JOB : "HKN Professional Development Events",
EVENT_TYPE.MISC : "HKN Miscellaneous Events",
}

GCAL.calendar_colors = {
EVENT_TYPE.CANDMAND : "#CC3333",   	# red
EVENT_TYPE.FUN : "#3366CC",		# blue
EVENT_TYPE.BIGFUN : "#94A2BE",		# blue
EVENT_TYPE.COMSERV : "#994499", 		# purple
EVENT_TYPE.DEPSERV : "#B08B59",		# brown
EVENT_TYPE.JOB : "#22AA99",		# teal
EVENT_TYPE.MISC : "#109618",		# green
}



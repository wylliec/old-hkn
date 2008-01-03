from hkn.enum import EnumType

RSVP_TYPE_NONE = 0
RSVP_TYPE_WHOLE = 1
RSVP_TYPE_BLOCK = 2

RSVP_TYPE = EnumType(NONE = RSVP_TYPE_NONE, WHOLE = RSVP_TYPE_WHOLE, BLOCK = RSVP_TYPE_BLOCK)
RSVP_TYPE.add_descriptions(((RSVP_TYPE.NONE, 'No RSVP'), (RSVP_TYPE.WHOLE, 'RSVP Whole Event'), (RSVP_TYPE.BLOCK, 'RSVP Time Block')))


EVENT_TYPE_CANDMAND = "CANDMAND"
EVENT_TYPE_FUN = "FUN"
EVENT_TYPE_BIGFUN = "BIGFUN"
EVENT_TYPE_COMSERV = "COMSERV"
EVENT_TYPE_DEPSERV = "DEPSERV"
EVENT_TYPE_JOB = "JOB"
EVENT_TYPE_MISC = "MISC"

EVENT_TYPE = EnumType(CANDMAND = EVENT_TYPE_CANDMAND, FUN = EVENT_TYPE_FUN, BIGFUN = EVENT_TYPE_BIGFUN, COMSERV = EVENT_TYPE_COMSERV, DEPSERV = EVENT_TYPE_DEPSERV, JOB = EVENT_TYPE_JOB, MISC = EVENT_TYPE_MISC)

EVENT_TYPE_DESCRIPTIONS = ( (EVENT_TYPE.CANDMAND, "Mandatory for Candidates"),(EVENT_TYPE.FUN, "Fun Activity"),
	(EVENT_TYPE.COMSERV, "Community Service"), (EVENT_TYPE.DEPSERV, "Departmental Service"),
	(EVENT_TYPE.JOB, "Professional Development"), (EVENT_TYPE.MISC, "Misc"), (EVENT_TYPE.BIGFUN, "Big Fun Activity") )
EVENT_TYPE.add_descriptions(EVENT_TYPE_DESCRIPTIONS)




# const pattern from some cookbook
class _const(object):
	class ConstError(TypeError): pass
	def __setattr__(self, name, value):
		if name in self.__dict__:
			raise self.ConstError, "can't rebind const (%s)" % name
		self.__dict__[name] = value
	def __delattr__(self, name):
		if name in self.__dict__:
			raise self.ConstError, "can't rebind const (%s)" % name
		raise NameError, name

RSVP_TYPE = _const()
EVENT_TYPE = _const()

RSVP_TYPE.NONE = 0
RSVP_TYPE.WHOLE = 1
RSVP_TYPE.BLOCK = 2

RSVP_TYPE.CHOICES = ((RSVP_TYPE.NONE, 'No RSVP'), (RSVP_TYPE.WHOLE, 'RSVP Whole Event'), (RSVP_TYPE.BLOCK, 'RSVP Time Block'))
RSVP_TYPE.CHOICES_DICT = {}
for choice in RSVP_TYPE.CHOICES:
	RSVP_TYPE.CHOICES_DICT[choice[0]] = choice[1]



EVENT_TYPE.CANDMAND = "CANDMAND"
EVENT_TYPE.FUN = "FUN"
EVENT_TYPE.BIGFUN = "BIGFUN"
EVENT_TYPE.COMSERV = "COMSERV"
EVENT_TYPE.DEPSERV = "DEPSERV"
EVENT_TYPE.JOB = "JOB"
EVENT_TYPE.MISC = "MISC"

EVENT_TYPE.CHOICES = [ (EVENT_TYPE.CANDMAND, "Mandatory for Candidates"),(EVENT_TYPE.FUN, "Fun Activity"),
	(EVENT_TYPE.COMSERV, "Community Service"), (EVENT_TYPE.DEPSERV, "Departmental Service"),
	(EVENT_TYPE.JOB, "Professional Development"), (EVENT_TYPE.MISC, "Misc"), (EVENT_TYPE.BIGFUN, "Big Fun Activity") ]


EVENT_TYPE.CHOICES_DICT = {}
for choice in EVENT_TYPE.CHOICES:
	EVENT_TYPE.CHOICES_DICT[choice[0]] = choice[1]


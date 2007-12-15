
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

MEMBER_TYPE = _const()

MEMBER_TYPE.ANONYMOUS = 0
MEMBER_TYPE.EXCANDIDATE = 5
MEMBER_TYPE.CANDIDATE = 10
MEMBER_TYPE.MEMBER = 15

# same thing
MEMBER_TYPE.FOGIE = 20
MEMBER_TYPE.EXOFFICER = 20

MEMBER_TYPE.OFFICER = 25



MEMBER_TYPE.CHOICES = ((MEMBER_TYPE.ANONYMOUS, "Anonymous"), (MEMBER_TYPE.EXCANDIDATE, "Ex-Candidate"), (MEMBER_TYPE.CANDIDATE, "Candidate"), (MEMBER_TYPE.MEMBER, "Member"), (MEMBER_TYPE.FOGIE, "Fogie"), (MEMBER_TYPE.OFFICER, "Officer"))

MEMBER_TYPE.CHOICES_DICT = {}
for choice in MEMBER_TYPE.CHOICES:
	MEMBER_TYPE.CHOICES_DICT[choice[0]] = choice[1]




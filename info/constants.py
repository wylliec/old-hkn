from hkn.constants import _const

MEMBER_TYPE = _const()
"""
Namespace for member type related constants. 

To import this constant namespace, do the following::
	from hkn.info.constants import MEMBER_TYPE

These constants include:
 	ANONYMOUS, EXCANDIDATE, CANDIDATE, MEMBER, FOGIE/EXOFFICER, OFFICER

Each of these constants has an associated integer value that is stored in the database.

In addition, there is a CHOICES list that is a list of (VALUE, DESCRIPTION)
tuples and a CHOICES_DICT dictionary that maps a VALUE to a DESCRIPTION.

Each member-type constant such as CANDIDATE can be accessed as such::
	>>>> MEMBER_TYPE.CANDIDATE
	10							# 10 is the integer representing CANDIDATE
	
Additionally, you can do the following to get the description::
	>>>> MEMBER_TYPE.CHOICES_DICT[MEMBER_TYPE.CANDIDATE]
	"Current Candidate"
	>>>> MEMBER_TYPE.CHOICES_DICT[person_object.member_type]
	"Current Officer"
			
"""
			

MEMBER_TYPE.ANONYMOUS = 0
"""An anonymous member: has never been a candidate"""

MEMBER_TYPE.EXCANDIDATE = 5
"""An ex-candidate: was a candidate at one point, but never became a member"""

MEMBER_TYPE.CANDIDATE = 10
"""A current candidate: is a candidate for this current semester"""

MEMBER_TYPE.MEMBER = 15
"""An HKN member: initiated at Berkeley at some point in the past"""

# same thing
MEMBER_TYPE.FOGIE = 20
"""A fogie: was an officer at some point but is no longer an officer"""

MEMBER_TYPE.EXOFFICER = 20
"""An ex-officer: same thing as fogie (same value-representation as well)"""

MEMBER_TYPE.OFFICER = 25
"""An officer: for the current semester"""


MEMBER_TYPE.CHOICES = ((MEMBER_TYPE.ANONYMOUS, "Anonymous"), (MEMBER_TYPE.EXCANDIDATE, "Ex-Candidate"), (MEMBER_TYPE.CANDIDATE, "Candidate"), (MEMBER_TYPE.MEMBER, "Member"), (MEMBER_TYPE.FOGIE, "Fogie"), (MEMBER_TYPE.OFFICER, "Officer"))
"""List of (value, description) tuples for all of the MEMBER_TYPE constants"""

MEMBER_TYPE.CHOICES_DICT = {}
"""Dictionary mapping values (e.g. MEMBER_TYPE.CANDIDATE) to description (e.g. "Current Candidate")"""

for choice in MEMBER_TYPE.CHOICES:
	MEMBER_TYPE.CHOICES_DICT[choice[0]] = choice[1]




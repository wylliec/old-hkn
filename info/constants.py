from nice_types import EnumType


            


ANONYMOUS = 0
"""An anonymous member: has never been a candidate"""

EXCANDIDATE = 5
"""An ex-candidate: was a candidate at one point, but never became a member"""

CANDIDATE = 10
"""A current candidate: is a candidate for this current semester"""

MEMBER = 15
"""An HKN member: initiated at Berkeley at some point in the past"""

# same thing
FOGIE = 20
"""A fogie: was an officer at some point but is no longer an officer"""

EXOFFICER = 20
"""An ex-officer: same thing as fogie (same value-representation as well)"""

OFFICER = 25
"""An officer: for the current semester"""

MEMBER_TYPE = EnumType(ANONYMOUS = ANONYMOUS, EXCANDIDATE = EXCANDIDATE, CANDIDATE = CANDIDATE, MEMBER = MEMBER, FOGIE = FOGIE, EXOFFICER = EXOFFICER, OFFICER = OFFICER)
"""
Namespace for member type related constants. 

To import this constant namespace, do the following::
    from hkn.info.constants import MEMBER_TYPE

These constants include:
    ANONYMOUS, EXCANDIDATE, CANDIDATE, MEMBER, FOGIE/EXOFFICER, OFFICER

Each of these constants has an associated integer value that is stored in the database.

Each member-type constant such as CANDIDATE can be accessed as such::
    >>>> MEMBER_TYPE.CANDIDATE
    10							# 10 is the integer representing CANDIDATE
    

Additionally, you can do the following to get the description::
    >>>> MEMBER_TYPE[person_object.member_status]
    "Officer"
    >>>> MEMBER_TYPE[MEMBER_TYPE.CANDIDATE]
    "Candidate"
    >>>> MEMBER_TYPE[10]
    "Candidate"	
    >>>> MEMBER_TYPE.describe("EXOFFICER")
    "Fogie"	
            

"""

MEMBER_TYPE.add_descriptions(((MEMBER_TYPE.ANONYMOUS, "Anonymous"), (MEMBER_TYPE.EXCANDIDATE, "Ex-Candidate"), (MEMBER_TYPE.CANDIDATE, "Candidate"), (MEMBER_TYPE.MEMBER, "Member"), (MEMBER_TYPE.FOGIE, "Fogie"), (MEMBER_TYPE.OFFICER, "Officer")))

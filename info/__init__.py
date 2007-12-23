

"""Module for general information on people, officers,
candidates,. Includes the following models:
- L{models.Person}
  The Person model. Contains personal information and HKN info (member status, etc.)
- L{models.ExtendedInfo}
  Each person also has an associated ExtendedInfo relation, which stores information
  that is not needed as frequently, such as mailing addresses, phone numbers, etc.
- L{models.CandidateInfo}
  Each Person who has gone through the candidate process will have an associated
  CandidateInfo. This contains information about their candidate semester, candidate
  committee, and general comments from the VP about their initiation.
- L{models.Position}
  There exists one Position object for each of the positions available in HKN:
  president, vp, rsec, csec, indrel, act, compserv, etc. etc.
- L{models.Officership}
  Tuple of (semester, position, person) that represents a position 'position'
  held by person 'person' in semester 'semester',

The views in this module handle the display of person information (lists of candidates,
lists of officers, etc.) as well as L{election <elect>} (i.e. handles creating the
appropriate officerships, etc. at the end of a semester for newly elected officers)
"""


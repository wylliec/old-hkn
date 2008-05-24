from nice_types import EnumType


EXAM = 0
RESUME = 1 
RSVP = 2
CHALLENGE = 3

DESCRIPTIONS = ((EXAM, "Exam File"), (RESUME, "Resume"), (RSVP, "RSVP"), (CHALLENGE, "Challenge"))

REQUEST_TYPE = EnumType(EXAM = EXAM, RESUME = RESUME, RSVP = RSVP, CHALLENGE = CHALLENGE)
REQUEST_TYPE.add_descriptions(DESCRIPTIONS)

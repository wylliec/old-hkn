from nice_types import EnumType

RSVP_TYPE_NONE = 0
RSVP_TYPE_WHOLE = 1
RSVP_TYPE_BLOCK = 2

RSVP_TYPE = EnumType(NONE = RSVP_TYPE_NONE, WHOLE = RSVP_TYPE_WHOLE, BLOCK = RSVP_TYPE_BLOCK)
RSVP_TYPE.add_descriptions(((RSVP_TYPE.NONE, 'No RSVP'), (RSVP_TYPE.WHOLE, 'RSVP Whole Event'), (RSVP_TYPE.BLOCK, 'RSVP Time Block')))

TRANSPORT_NEED_RIDE = -1
TRANSPORT_SMALL = 4
TRANSPORT_SEDAN = 5
TRANSPORT_VAN = 7
TRANSPORT_SELF = 0

TRANSPORT = EnumType(NEED_RIDE=TRANSPORT_NEED_RIDE, SEDAN=TRANSPORT_SEDAN, VAN=TRANSPORT_VAN, SELF=TRANSPORT_SELF, SMALL=TRANSPORT_SMALL)
TRANSPORT.add_descriptions(((TRANSPORT.NEED_RIDE, "I need a ride"), 
                            (TRANSPORT.SMALL, "I have a small sedan (4 seats)"), 
                            (TRANSPORT.SEDAN, "I have a sedan (5 seats)"), 
                            (TRANSPORT.VAN, "I have a minivan (7 seats)"), 
                            (TRANSPORT.SELF, "Don't worry about me")))


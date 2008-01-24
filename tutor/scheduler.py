#holds methods used to calculate a schedule given preference and scoring information

from hkn.tutor.constants import *
from hkn.utils import NiceDict

import random

#"preference detail" is a dictionary {person, preference} for some particular slot
#"slot" is defined by the caller, but uniquely identifies a specific slot to be assigned
#  for hkn tutoring, it is a dictionary with day, time, and office

def generateSchedule(availabilitiesBySlot = NiceDict([]),
                     adjacencyChecker = areAdjacentHours,
                     slotsByPerson = NiceDict(DEFAULT_HOURS, HOUR_EXCEPTIONS),
                     scoring = {"correct_office":SCORE_CORRECT_OFFICE,
                                "miss_penalty":SCORE_MISS_PENALTY,
                                "adjacent":SCORE_ADJACENT,
                                "preference":SCORE_PREFERENCE},
                     options = NiceDict(False,
                                        {"random_seed":False
                                         })
                     ):
    """
    Returns:
        Dictionary with:
            -assignments: Dictionary mapping from slot to "preference detail" for
                person assigned to that slot
            -happiness: Dictionary mapping from person to "happiness info".  Also includes
                key "net" for overall happiness.
                -"happiness info" - Dictionary with keys:
                    -net - this person's overall happiness
                    -first_choices - number of first choice assignments
                    -second_choices - number of second choice assignments
                    -correct_office_count - number of assignments to preferred office
                    -missing - [target - actual] slots assigned to this person
                    -adjacencies - number of pairs of adjacent time slots
    Arguments:
        -availabilitiesBySlot: Dictionary from slot to list of "preference details"
        -slotsByPerson: Dictionary from person to number of slots that person should be
            assigned
        -adjacencyChecker - function that takes 2 slots and returns True if they are
            adjacent, False otherwise
        -scoring: Dictionary that describes how to score utility / happiness.  Includes:
            -correct_office: score for each assignment to the correct office
            -miss_penalty: penalty for each assignment more or less than what is correct
            -adjacent: score for each adjacency (pair of adjacent slots for 1 person)
            -preference: Dictionary that maps from preference level (int) to score for
                assignment to a slot of that preference level
        -options: Dictionary mapping from options names to values
            -random_seed: provide a random seed for calculations
    """
    if not options['random_seed']:
        random.seed() #uses system time or an operating system's source of randomness
    else:
        random.seed(randomSeed)
    
    #INCOMPLETE
    raise "Not yet implemented"


def areAdjacentHours(slotA, slotB):
    """
    Returns whether slotA and slotB have adjacent hours, assuming slot is defined as
    a dictionary with the key "time" and values according to TUTORING_HOURS
    
    Raises exception if times are identical or cannot find either time in TUTORING_HOURS
    """
    justSeen = False
    slotATime = slotA['time']
    slotBTime = slotB['time']
    if slotATime == slotBTime:
        raise "Slot A and Slot B have the same time!"
    for time in TUTORING_HOURS:
        if time == slotATime or time == slotBTime:
            if justSeen:
                return True
            else:
                justSeen = True
        else:
            if justSeen:
                return False
    raise "Cannot find time for neither " + str(slotA) + " nor " + str(slotB)
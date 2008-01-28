#holds methods used to calculate a schedule given preference and scoring information

from hkn.tutor.constants import *
from hkn.utils import NiceDict

import random

"""
"preference detail" is a dictionary {person, preference} for some particular slot

"slot" is a dictionary with day, time, and office
  
"costs" is a dicitonary with keys "base", "correct_office", "adjacent", and "preference".
  "preference" is a dictionary from level of preference to bonus for that preference.
  Costs are calculated using costs['base'] - [all applicable bonuses].
  Example:
    Cost to add a preference level 2 slot to the correct office that is adjacent to 1 time:
      costs['base'] - costs['preference'][2] - costs['correct_office'] -  1 * costs['adjacent']

"state" is a dictionary from slots to assignments, None for none assigned

"""

class State(dict):
    """
    Simply a dictionary with an instance variable "meta" that can be used for storing
    useful metadata about this state.  meta is copied (maybe shallow) when State is copied.
    """
    def __init__(self, *a, **kw):
        self.meta = {}#should be a shallow dictionary
        dict.__init__(self, *a, **kw)
    
    def copy(self):
        return self.__copy__(self)
    
    def __copy__(self):
        temp = type(self)(self)
        temp.meta = self.meta.copy()
        return temp
    
    def __deepcopy__(self, memo):
        import copy
        temp = type(self)(self.defaultValue,
                          copy.deepcopy(self.items()))
        temp.meta = self.meta.copy()
        return temp
    def __repr__(self):
        return 'NiceDict(%s, %s)' % (self.defaultValue,
                                        dict.__repr__(self))

def are_adjacent_hours(slotA, slotB):
    """
    Returns whether slotA and slotB have adjacent hours, assuming slot is defined as
    a dictionary with the key "time" and values according to TUTORING_HOURS
    
    Does not care if times are in different offices
    
    Raises exception if times are identical or cannot find either time in TUTORING_HOURS
    """
    if slotA['day'] != slotB['day']:
        return False
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

def generate_schedule(availabilitiesBySlot = NiceDict([]),
                      adjacency_checker = are_adjacent_hours,
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
    
    INCOMPLETE - raises an error if called
    
    Returns:
        Dictionary with:
            assignments: Dictionary mapping from slot to "preference detail" for
                person assigned to that slot
            happiness: Dictionary mapping from person to "happiness info".  Also includes
                key "net" for overall happiness.
                "happiness info" - Dictionary with keys:
                    net - this person's overall happiness
                    first_choices - number of first choice assignments
                    second_choices - number of second choice assignments
                    correct_office_count - number of assignments to preferred office
                    missing - [target - actual] slots assigned to this person
                    adjacencies - number of pairs of adjacent time slots
    Arguments:
        availabilitiesBySlot: Dictionary from slot to list of "preference details"
        slotsByPerson: Dictionary from person to number of slots that person should be
            assigned
        adjacency_checker - function that takes 2 slots and returns True if they are
            adjacent, False otherwise
        scoring: Dictionary that describes how to score utility / happiness.  Includes:
            correct_office: score for each assignment to the correct office
            miss_penalty: penalty for each assignment more or less than what is correct
            adjacent: score for each adjacency (pair of adjacent slots for 1 person)
            preference: Dictionary that maps from preference level (int) to score for
                assignment to a slot of that preference level
        options: Dictionary mapping from options names to values
            random_seed: provide a random seed for calculations
    """
    if not options['random_seed']:
        random.seed() #uses system time or an operating system's source of randomness
    else:
        random.seed(randomSeed)
    
    """
    see documentation at top for costs
    """
    costs = {'base': scoring['correct_office'] +
                     scoring['adjacent'] * 2 +
                     max(scoring['preference'].values()) +
                     1,
             'correct_office': scoring['correct_office'],
             'adjacent': scoring['adjacent'],
             'preference': scoring['preference']}
    
    #INCOMPLETE
    raise "Not yet implemented"

def get_successors(state=State(),
                   availabilitiesBySlot=NiceDict([]),
                   slotsByPerson=NiceDict(DEFAULT_HOURS, HOUR_EXCEPTIONS)):
    """
    Returns: list of states that are successsors to the given state, or empty list if none
    """
    return []

def heuristic(state=State(), costs=NiceDict(0, {'base':1}), availabilitiesBySlot = NiceDict([])):
    """
    Returns: integer estimate of optimal future costs from this state
    Arguments:
        state - dictionary from slots to assignments, None for none assigned
        costs - see documentation at top
        availabilitiesBySlot - see documentation for generateSchedule
    """
    return 0

def hillClimb(initialState=State(),
              costs=NiceDict(0, {'base':1}),
              slotsByPerson=NiceDict(DEFAULT_HOURS, HOUR_EXCEPTIONS),
              adjacency_checker=are_adjacent_hours,
              availabilitiesBySlot=NiceDict([])):
    """
    Returns: list of [best found, cost of best found]
    INCOMPLETE - feel free to change the return or argument format, just be sure to tell me -Darren
    """
    return [initialState, get_total_cost(initialState)]




#helpful methods below
def get_cost(initialState=State(),
            slot={"day":"Monday", "time":"1-2", "office":SODA},
            person="Person Object",
            costs=NiceDict(0, {'base':1}),
            adjacency_checker=are_adjacent_hours,
            availabilitiesBySlot=NiceDict([])):
    """
    get the cost of making the assignment in the given slot to the given person,
    with the given initial state.
    """
    cost = costs['base']
    for key in initialState:
        if key != slot and initialState[key] == person and adjacency_checker(key, slot):
            cost -= costs['adjacent']
    found = False
    for detail in availabilitiesBySlot[slot]:
        if detail['person'] == person:
            cost -= costs['correct_office']
            cost -= costs['preference'][detail['preference']]
            found = True
            break
    if not found:
        otherOfficeSlot = {'day':slot['day'], 'time':slot['time']}
        if slot[CORY]:
            otherOfficeSlot['office'] = SODA
        else:
            otherOfficeSlot['office'] = CORY
        for detail in availabilitiesBySlot[otherOfficeSlot]:
            if detail['person'] == person:
                cost -= costs['preference'][detail['preference']]
                break
    return cost

def get_cost_difference(oldState=State(),
                        newState=State(),
                        costs=NiceDict(0, {'base':1}),
                        adjacency_checker=are_adjacent_hours,
                        availabilitiesBySlot=NiceDict([])):
    """
    Returns (total cost of given newState) - (total cost of given oldState)
    """
    commonAncenstor = {}
    for key in oldState:
        oldPerson = oldState[key]
        if newState[key] == oldPerson:
            commonAncestor[key] = oldPerson
    
    costToOldState = get_total_cost(state=oldState,
                                    costs=costs,
                                    adjacency_checker=adjacency_checker,
                                    availabilitiesBySlot=availabilitiesBySlot,
                                    baseState=commonAncestor)
    costToNewState = get_total_cost(state=newState,
                                    costs=costs,
                                    adjacency_checker=adjacency_checker,
                                    availabilitiesBySlot=availabilitiesBySlot,
                                    baseState=commonAncestor)
    return costToNewState - costToOldState

def get_total_cost(state=State(),
                   costs=NiceDict(0, {'base':1}),
                   adjacency_checker=are_adjacent_hours,
                   availabilitiesBySlot=NiceDict([]),
                   baseState=None):
    """
    WARNING: this can be very expensive.  Use as infrequently as possible.
    
    if baseState is provided, will calculate cost from baseState to given state
    """
    cost = 0
    tempState = None #state so far
    
    if baseState:
        tempState = baseState.copy()
    else:
        tempState=State()
        for key in state:
            tempState[key] = None
    
    for key in state:
        if tempState[key] == state[key]:
            continue
        cost += get_cost(initialState=tempState,
                         slot=key,
                         person=state[key],
                         costs=costs,
                         adjacency_checker=adjacency_checker,
                         availabilitiesBySlot=availabilitiesBySlot)
        tempState[key] = state[key]
    
    return cost
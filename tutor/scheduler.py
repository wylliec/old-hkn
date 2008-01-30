#holds methods used to calculate a schedule given preference and scoring information

from hkn.tutor.constants import *
from hkn.utils import NiceDict

import heapq, random, sys

"""
Notes, terms, and oddities:

If an office is preferred, subtract 0.5 from the preference level.  A preference detail will exist
for unpreferred offices at days/times that people can make.  Lower preference is always better.

"preference detail" is a list [person, preference] for some particular slot
  
"costs" is a dicitonary with keys "base", "correct_office", "adjacent", and "preference".
  "preference" is a dictionary from level of preference to bonus for that preference.
  Costs are calculated using costs['base'] - [all applicable bonuses].
  Example:
    Cost to add a preference level 2 slot to the correct office that is adjacent to 1 time:
      costs['base'] - costs['preference'][2] - costs['correct_office'] -  1 * costs['adjacent']

"state" is a dictionary from slots to assignments, None for none assigned

"""

class Slot:
    def __init__(self, day, time, office):
        self.day = day
        self.time = time
        self.office = office
    
    def __hash__(self):
        ret = 0
        if self.office == SODA:
            ret += 1
        return ret + self.day.__hash__() * 203 + self.time.__hash__() * 3

    def __str__(self):
        return self.day + ' ' + self.time + ' ' + self.office
    
    def __repr__(self):
        return "Slot<%s %s %s>" % (self.day, self.time, self.office)
    
    def __eq__(self, other):
        otherstuff = dir(other)
        return 'day' in otherstuff and 'time' in otherstuff and 'office' in otherstuff and \
            self.day == other.day and self.time == other.time and self.office == other.office
    
class State(dict):
    """
    Simply a dictionary with an instance variable "meta" that can be used for storing
    useful metadata about this state.  noneCount and meta is copied (maybe shallow) when
    State is copied
    
    States may be compared, in which case they are compared by estCost()
    
    States may be hashed (unlike dictionaries)
    
    also has makeChild, estCost, isGoal, and initialize_keys methods
    
    meta may contain:
        parent - parent state, will be None if no known parent.  Always present.
        cost - cost of state
        heuristic - heuristic of state
        children - all (as of last calculated) unvisited successors
        slotAssigned - slot assigned between parent and this state
        personAssigned - person assigned between parent and this state
    """
    def __init__(self, *a, **kw):
        self.meta = {'parent':None}#should be a shallow dictionary, i.e. all keys and values are strings or numbers
        self.noneCount = 0
        dict.__init__(self, *a, **kw)
    
    def initialize_keys(self, keys):
        """
        For each key in keys and not in self, adds key to self with given value (default None)
        
        returns self
        """
        for key in keys:
            if key not in self:
                self[key] = None
        return self
    
    def makeChild(self, slot, person):
        """
        makes a Child (successor) of this state.  Copies the state, adds an assignment in
        given slot to given person, removes incorrect info from meta and fixes the parent
        pointer.  Sets meta info about the slot and person just assigned.
        """
        ret = self.copy()
        ret[slot] = person
        meta = ret.meta
        meta['parent'] = self
        meta['slotAssigned'] = slot
        meta['personAssigned'] = person
        if 'children' in meta:
            del meta['children']
        if 'cost' in meta:
            del meta['cost']
        if 'heuristic' in meta:
            del meta['heuristic']
        
        return ret
    
    def __setitem__(self, key, value):
        if key in self:
            if self[key] == None and value != None:
                self.noneCount -= 1
            elif self[key] != None and value == None:
                self.noneCount += 1
        elif value == None:
            self.noneCount += 1
        dict.__setitem__(self, key, value)
    
    def estCost(self):
        return self.meta['cost'] + self.meta['heuristic']
    
    def isGoal(self):
        """
        this is a goal if all keys are not None and there is at least one key
        """
        return len(self) > 0 and self.noneCount == 0
        
    def copy(self):
        return self.__copy__()
    
    def __copy__(self):
        temp = type(self)(self)
        temp.meta = self.meta.copy()
        temp.noneCount = self.noneCount
        return temp
    
    def __deepcopy__(self, memo):
        import copy
        temp = type(self)(self.defaultValue,
                          copy.deepcopy(self.items()))
        temp.meta = self.meta.copy()
        return temp
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return 'State(meta:%s, assignments:%s)' % (self.meta.__repr__(),
                                        dict.__repr__(self))
    
    def __eq__(self, other):
        """
        does NOT compare meta, only keys
        """
        if type(self) != type(other) or len(self) != len(other):
            return False
        for key in self:
            if key not in other or self[key] != other[key]:
                return False
        return True
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return self.estCost() < other.estCost()
    def __le__(self, other):
        return self.estCost() <= other.estCost()
    def __gt__(self, other):
        return self.estCost() > other.estCost()
    def __ge__(self, other):
        return self.estCost() >= other.estCost()
    
    def __hash__(self):
        ret = 0
        for key in self:
            ret += key.__hash__() * str(self[key]).__hash__()
        return ret
    
class PriorityQueue:
  """
    Implements a priority queue data structure. Each inserted item
    has a priority associated with it and the client is usually interested
    in quick retrieval of the lowest-priority item in the queue. This
    data structure allows O(1) access to the lowest-priority item.
    
    This was written by cs188 staff for the 2007 fall semester at
    University of California, Berkeley, 94720.
  """
    
  def __init__(self):
    """
      heap: A binomial heap storing [priority,item]
      lists. 
      
      dict: Dictionary storing item -> [priorirty,item]
      maps so we can reach into heap for a given 
      item and update the priorirty and heapify
    """
    self.heap = []
    self.dict = {}
      
  def push(self,item,priority):
    """
        Sets the priority of the 'item' to
    priority. If the 'item' is already
    in the queue, then its key is changed
    to the new priority, regardless if it
    is higher or lower than the current 
    priority.
    """
    if item in self.dict:
      self.dict[item][0] = priority
      heapq.heapify(self.heap)
    else:
      pair = [priority,item]
      heapq.heappush(self.heap,pair)
      self.dict[item] = pair
      
  def getPriority(self,item):
    """
        Get priority of 'item'. If 
    'item' is not in the queue returns None
    """
    if not item in self.dict:
      return None
    return self.dict[item][0]
      
  def pop(self):
    """
      Returns lowest-priority item in priority queue, or
      None if the queue is empty
    """
    if self.isEmpty(): return None
    (priority,item) = heapq.heappop(self.heap)
    del self.dict[item]
    return item  
  
  def isEmpty(self):
    """
        Returns True if the queue is empty
    """
    return len(self.heap) == 0

class StateTracker:
    """
    Tracks all states.  Knows the tree of execution and can find unexplored
    state with lowest cost.  Filters successors so only returns unvisited
    successors with cost <= maximumCost (when maximumCost is positive).
    
    The function pointer get_successors must take a single argument "state"
    
    All states pushed into StateTracker are keys in visited.  Visited states
    evaluate to true in visited[state][1].  The key is stored in visited[state][0]
    
    All states generated by filteredSuccessors are placed as keys into visited.
    """
    def __init__(self,
                 maximumCost=0,
                 get_successors=lambda state:[],
                 heuristic=lambda state: 0,
                 get_cost=lambda state, slot, person:1):
        self.priorityQueue = PriorityQueue()
        self.secondaryPriorityQueue = PriorityQueue() #stores states with costs over maximumCost
        
        self.visited = NiceDict(["key",False])
        
        self.maximumCost = maximumCost
        self.get_successors = get_successors
        self.heuristic = heuristic
        self.get_cost = get_cost
        
        self.stats = {'pushed':0,
                      'popped':0,
                      'visited':0,
                      'backtracks':0,
                      'successors':0}
    
    def push(self, state):
        """
        Push an unvisited state into the StateTracker.  If state is already in
        StateTracker, does nothing.  All identical states have the same cost.
        All states pushed must already have meta['cost'] and meta['heuristic']
        """
        if state in self.visited:
            return
        self.priorityQueue.push(state, state.estCost())
        self.visited[state] = [state, False]
        self.stats['pushed'] += 1
    
    def filtered_successors(self, state):
        """
        Returns list of successor States of the given state, filtering out states with
        too high of a cost + heuristic and visited states
        
        All states generated by this method are stored in the priorityQueue and kept as
        keys in visited
        
        Does not recalculate cost or heuristic for states that are already known.
        """
#        print "\tfiltered_successors called"
        allSuccessors = None
        knowAllCosts = False
        if 'children' in state.meta:
            allSuccessors = state.meta['children']
            knowAllCosts = True
#            print "using %s children" % len(allSuccessors)
        else:
            allSuccessors = self.get_successors(state)
#            print "found %s successors" % len(allSuccessors)
        children = []
        ret = []
        returned = 0
        for s in allSuccessors:
            if not knowAllCosts:
                if s in self.visited:
                    visitedInfo = self.visited[s]
                    if visitedInfo[1]:
#                        print '--ignoring successor, already visited'
                        continue #don't return one we've visited
                    #replace s with the one in visited, which already has cost and heuristic calculated
                    s = visitedInfo[0]
                else:
                    #calculate cost and heuristic
                    s.meta['cost'] = state.meta['cost'] + self.get_cost(state,
                                                                        s.meta['slotAssigned'],
                                                                        s.meta['personAssigned'])
                    s.meta['heuristic'] = self.heuristic(s)
                    
                    #store this state
                    self.push(s)
            elif s in self.visited and self.visited[s][1]:
#                print '--ignoring successor, already visited (case 2)'
                continue #don't return one we've visited
            
            #all nonvisited children are saved, in case maximumCost is increased
            children.append(s)
            
            #only add s to ret if under max cost or max cost is disabled (ie not > 0)
            if self.maximumCost <= 0 or s.estCost() < self.maximumCost:
                ret.append(s)
                returned += 1
        
        state.meta['children'] = children
        
        if not knowAllCosts:
            self.stats['successors'] += returned

#        print "\tfiltered_successors returning %s" % ret
        
        return ret
    
    def pop(self):
        """
        Returns a "good" candidate for exploring.  Currently just the lowest cost state
        that has yet to be visited.  Returns None when no states left.
        """
        self.stats['popped'] += 1
        #TODO consider preferring deeper ones
        ret = self.priorityQueue.pop()
        while ret != None and self.visited[ret][1]:
            ret = self.priorityQueue.pop()
        if ret != None and self.maximumCost > 0 and ret.estCost() > self.maximumCost:
            #store it for later just in case we raise maximumCost again
            self.secondaryPriorityQueue.push(ret, ret.estCost())
            #nothing else in this priorityQueue will have lower cost than maximumCost
            return None
        return ret
    
    def backtrack(self, state):
        """
        Returns the next state that would be found via backtracking the pseudo DFS.  If
        cannot backtrack further, returns None.
        """
#        print "\tbacktrack called"
        self.stats['backtracks'] += 1
        parent = state
        successors = []
        while len(successors) == 0:
#            print "\tbacktracking from state %s" % dict(parent)
            if parent.meta['parent'] == None:
                return None #cannot backtrack further
            parent = parent.meta['parent']
            successors = self.filtered_successors(parent)
        return min(successors)
    
    def visit(self, state):
        """
        mark state as visited
        """
        if not self.visited[state][1]:
            self.stats['visited'] += 1
            self.visited[state] = [state, True]
    
    def increaseMaximumCostTo(self, newMaxCost):
        if self.maximumCost > newMaxCost:
            raise "this should only be called to increase, not decrease maximumCost"
        self.maximumCost = newMaxCost
        elem = self.secondaryPriorityQueue.pop()
        while elem != None and elem.estCost() <= self.maximumCost:
            self.priorityQueue.push(elem, elem.estCost())
            elem = self.secondaryPriorityQueue.pop()
        
        if elem != None:
            self.secondaryPriorityQueue.push(elem, elem.estCost())

def are_adjacent_hours(slotA, slotB):
    """
    Returns whether slotA and slotB have adjacent hours, assuming slot is defined as
    a dictionary with the key "time" and values according to TUTORING_TIMES
    
    Does not care if times are in different offices.  Identical times are not adjacent.
    
    Raises exception if cannot find either time in TUTORING_TIMES
    """
    if slotA.day != slotB.day:
        return False
    justSeen = False
    slotATime = slotA.time
    slotBTime = slotB.time
    if slotATime == slotBTime:
        return False
    for time in TUTORING_TIMES:
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
                                 "adjacent_same_office":SCORE_ADJACENT_SAME_OFFICE,
                                 "preference":SCORE_PREFERENCE},
                      options = NiceDict(False,
                                         {"random_seed":False
                                          })
                      ):
    """
    Returns:
        list of best states found, from best to worst.
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
            adjacent_same_office: score for each adjacency (pair of adjacent slots for 1 person)
                that are both in the same office.  Overrides adjacent.
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
    costs = {'base': max(scoring['adjacent'], scoring['adjacent_same_office']) * 2 +
                     max(scoring['preference'].values()) +
                     scoring['correct_office'] +
                     1,
             'adjacent': scoring['adjacent'],
             'adjacent_same_office': scoring['adjacent_same_office']}
    
    costs['preference'] = {}
    for int_key in scoring['preference']:
        costs['preference'][int_key] = scoring['preference'][int_key]
        costs['preference'][int_key - 0.5] = scoring['preference'][int_key] + scoring['correct_office']
    
#    print "\tcosts: %s" % costs
    
    my_get_successors = lambda state: get_successors(state,
                                                     availabilitiesBySlot = availabilitiesBySlot,
                                                     slotsByPerson = slotsByPerson)
    
    my_heuristic = lambda state: heuristic(state=state,
                                           costs=costs,
                                           availabilitiesBySlot=availabilitiesBySlot)
    
    my_hill_climb = lambda state: hill_climb(initialState=state,
                                            costs=costs,
                                            slotsByPerson=slotsByPerson,
                                            adjacency_checker=adjacency_checker,
                                            availabilitiesBySlot=availabilitiesBySlot)
    
    my_get_cost = lambda state, slot, person: get_cost(initialState=state,
                                                       slot=slot,
                                                       person=person,
                                                       costs=costs,
                                                       adjacency_checker=adjacency_checker,
                                                       availabilitiesBySlot=availabilitiesBySlot)
    
    
    state = options['initialState']
    if not state:
        state = State().initialize_keys(availabilitiesBySlot)
        state.meta['parent'] = None
        state.meta['cost'] = 0
        state.meta['heuristic'] = my_heuristic(state)
    
    stateTracker = StateTracker(
                        get_successors = my_get_successors,
                        heuristic=my_heuristic,
                        get_cost=my_get_cost)
    stateTracker.push(state)
    
    iterations = 0
    maxIterations = 10**4 #TODO change!
    bestSoFar = []
    goalsFound = 0
    maxKept = 100
    while iterations < maxIterations and state != None: #TODO change!
        if iterations % 1000 == 0:
            print "\titeration: %d, best goal of %d: %d" % (iterations, goalsFound, stateTracker.maximumCost)
#            print "\tstats: %s" % stateTracker.stats
        iterations += 1
        stateTracker.visit(state)
        
        if state.isGoal():
            tmp = state.copy()
            tmp.meta['parent'] = 'removed'
#            print "\tfound goal: %s" % tmp
            
            goalsFound += 1
            
            #no successors, this is a goal state.  Try to find a better one by hill climbing
            state = my_hill_climb(state)
            
            #tell stateTracker about this state and the new max cost
            stateTracker.push(state)
            stateTracker.visit(state)
            stateTracker.maximumCost = state.estCost()
            
            #add this new state to our list of bestSoFar
            bestSoFar.insert(0, state)
            if len(bestSoFar) > maxKept:
                bestSoFar.pop() #dump least good in bestSoFar
            
            state = stateTracker.pop() #get some other "good" state from stateTracker
        else:
#            print "\tlooking for successors"
            successors = stateTracker.filtered_successors(state)
            if len(successors) == 0:
#                print "\tbacktracking"
                state = stateTracker.backtrack(state)
                if state == None:
#                    print "\tbacktrack failed, looking for new state"
                    state = stateTracker.pop()
#                    if state == None:
#                        print "\tstate is now None"
#                    else:
#                        print "\tstate is now %s" % dict(state)
            else:
                state = min(successors)
            
    print "\tstateTracker stats: %s" % str(stateTracker.stats)
    print "\tfound %d goals in %d iterations" % (goalsFound, iterations)
    bestCosts = "best goals had costs: ["
    for goal in bestSoFar:
        bestCosts += str(goal.meta['cost']) + ","
    print bestCosts[:-1] + ']'
    
    return bestSoFar

def get_successors(state=State(),
                   availabilitiesBySlot=NiceDict([]),
                   slotsByPerson=NiceDict(DEFAULT_HOURS, HOUR_EXCEPTIONS)):
    """
    Returns: list of states that are successsors to the given state, or empty list if none.
    Each state will have 'parent', 'slotAssigned', and 'personAssigned', but missing
    'cost' and 'heuristic' info in the meta
    
    slotAssigned and personAssigned are the slot / person assigned when coming from parent
    
    INCOMPLETE - this is a "correct" but dumb version
    """
    ret = []
    emptySlot = None
    numAssigned = NiceDict(0)
    for slot in state:
        person = state[slot]
        if person == None:
            emptySlot = slot
        else:
            if person not in numAssigned:
                numAssigned[person] = 1
            else:
                numAssigned[person] += 1
    
    for person in [detail[0] for detail in availabilitiesBySlot[emptySlot]]:
        if numAssigned[person] >= slotsByPerson[person]:
            continue #person cannot tutor any more, so assign to other
        successor = state.makeChild(emptySlot, person)
        ret.append(successor)
    
    if len(ret) == 0 and not state.isGoal():
        raise "returned no successors for non-goal state %s" % dict(state)
    if len(ret) > 0:
        for e in ret:
            if state.noneCount <= e.noneCount:
                raise "successor does not have more assignments than parent"
    
    return ret

def heuristic(state=State(), costs=NiceDict(0, {'base':1}), availabilitiesBySlot = NiceDict([])):
    """
    Returns: integer estimate of optimal future costs from this state
    Arguments:
        state - dictionary from slots to assignments, None for none assigned
        costs - see documentation at top
        availabilitiesBySlot - see documentation for generateSchedule
    """
    return 0

def hill_climb(initialState=State(),
              costs=NiceDict(0, {'base':1}),
              slotsByPerson=NiceDict(DEFAULT_HOURS, HOUR_EXCEPTIONS),
              adjacency_checker=are_adjacent_hours,
              availabilitiesBySlot=NiceDict([])):
    """
    Returns: list of best state found, with cost info in the meta.  If did any hill climbing,
    meta['parent'] is None.  Returned state must have meta['cost'] be the correct cost, and
    must have meta['heuristic'] be 0, since this is a goal state.
    
    INCOMPLETE - feel free to change the return or argument format, just be sure to tell me -Darren
    """
    
    #I suggest using the below my_get_cost_difference to consider hill climbing among neighbors.
    # get_cost_difference is faster than get_total_cost.
    # You can be even faster if you can provide the common ancestor.
    my_get_cost_difference = lambda oldState, newState, commonAncestor = None: get_cost_difference(
                                                                                   oldState=oldState,
                                                                                   newState=newState,
                                                                                   commonAncestor=commonAncestor,
                                                                                   costs=costs,
                                                                                   adjacency_checker=adjacency_checker,
                                                                                   availabilitiesBySlot=availabilitiesBySlot)
    
    return initialState




#helpful methods below
def get_cost(initialState=State(),
            slot=Slot("Monday", "1-2", SODA),
            person="Person Object",
            costs=NiceDict(0, {'base':1}),
            adjacency_checker=are_adjacent_hours,
            availabilitiesBySlot=NiceDict([])):
    """
    get the cost of making the assignment in the given slot to the given person,
    with the given initial state.
    """
    
#    raise "I have a bug in this code, doesn't prefer adjacent slots"
    
#    adjacencies = 0 #TODO remove
    
    cost = costs['base']
    for key in initialState:
        if key != slot and initialState[key] == person and adjacency_checker(key, slot):
            if key.office == slot.office:
                cost -= costs['adjacent_same_office']
            else:
                cost -= costs['adjacent']
#            adjacencies += 1 #TODO remove
    found = False
    for detail in availabilitiesBySlot[slot]:
        if detail[0] == person:
            cost -= costs['preference'][detail[1]]
            found = True
            break
    
    #TODO remove below
#    print "\tget_cost returning cost %d, found %d adjacencies for assigning (%s, %s) to state %s" % (cost, adjacencies, slot, person, dict(initialState))
    
    return cost

def get_cost_difference(oldState=State(),
                        newState=State(),
                        costs=NiceDict(0, {'base':1}),
                        adjacency_checker=are_adjacent_hours,
                        availabilitiesBySlot=NiceDict([]),
                        commonAncestor = None):
    """
    Returns (total cost of given newState) - (total cost of given oldState)
    
    More efficient than calling get_total_cost on each
    """
    if commonAncestor == None:
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

def run_tests(verbose = False):
    """
    runs tests for scheduler
    """
    
    PASSED = [0]
    FAILED = [0]
    def run_test_exact(expected, availabilitiesBySlot, slotsByPerson):
        ret = "Test did not finish"
        try:
            ret = generate_schedule(availabilitiesBySlot = availabilitiesBySlot,
                      slotsByPerson = slotsByPerson)
            
            if verbose: print "generate_schedule returning %s"  % ret
            
            if ret == expected:
                print "passed test\n"
                PASSED[0] += 1
                return
        except:
            print "Unexpected error:", sys.exc_info()[0]
        print "failed test, expected %s\n\t but got %s\n" % (expected, ret)
        FAILED[0] += 1
    def run_test(maxCost, minLength, availabilitiesBySlot, slotsByPerson):
        ret = "Test did not finish"
        try:
            ret = generate_schedule(availabilitiesBySlot = availabilitiesBySlot,
                      slotsByPerson = slotsByPerson)
            for e in ret:
                e.meta['parent'] = 'removed'
            if verbose: print "generate_schedule returning %s"  % ret
            
            if len(ret) >= minLength and ret[0].estCost() <= maxCost:
                print "passed test\n"
                PASSED[0] += 1
                return
        except:
            print "Unexpected error:", sys.exc_info()
            raise
        print "failed test, expected maxCost %s minLength %s\n\t but got %s\n" % (maxCost, minLength, ret)
        FAILED[0] += 1    
    
    def parse_into_availabilities_by_slot(coryTimes, sodaTimes):
        """
        converts strings into availabilitiesBySlot object.
        Expects the string to be of the form:
        
            each line corresponds to one time period
            within each line, days are separated by commas
            within each day-hour section, preference details are separated by spaces
            each preference detail takes the form: (PersonName)(preference)[p if preferred office]
            
            example for people named A, B, C, and D (you may use longer names):
            
            corytimes =
                A1p B1p C1p D2, A1p B2p C1p D1\n
                A1p B2p C2p D2, A2p B1p C1p D1
            
            ->
            
            {Slot<Monday 11a-12 Cory>: [(A, 0.5), (B, 0.5), (C, 0.5), (D, 2)],
             ...
            }
        """
        ret = {}
        office = CORY
        for timesString in (coryTimes, sodaTimes):
            hourIndex = 0
            for hourAvailString in timesString.split('\n'):
                dayIndex = 0
                for dayAvailString in hourAvailString.split(','):
                    for detailString in dayAvailString.strip().split(' '):
#                        print "detailString: %s" % detailString
                        if detailString[-1:] == 'p':
                            preference = int(detailString[-2:-1]) - 0.5
                            person = detailString[:-2]
                        else:
                            preference = int(detailString[-1:])
                            person = detailString[:-1]
                        slot = Slot(TUTORING_DAYS[dayIndex], TUTORING_TIMES[hourIndex], office)
                        if slot not in ret:
                            ret[slot] = []
                        ret[slot].append((person, preference))
                    #end for detailString
                    dayIndex += 1
                #end for dayAvailString
                hourIndex += 1
            #end for hourAvailString
            office = SODA
        #end for timesString
        
        return ret
    
    
    print "Running tests on scheduler..."
    
    
    mondayMorningSodaSlot = Slot(TUTORING_DAYS[0], TUTORING_TIMES[0], SODA)
    
    print "test 1: one slot, one person, one availability"
    
    availabilitiesBySlot = {mondayMorningSodaSlot: [
                                            ['OnlyPerson', 0.5],
                                            ]}
    slotsByPerson = {'OnlyPerson':1}
    expected = [State({mondayMorningSodaSlot:'OnlyPerson'})]
    
    run_test_exact(expected, availabilitiesBySlot, slotsByPerson)
    
    
    
    print "test 2: four slots, two people, all available"
    
    avails = [("personA", 0.5), ("personB", 0.5)]
    slots = []
    for i in range(1):
        for office in (SODA, CORY):
            for j in range(2):
                slots.append(Slot(TUTORING_DAYS[i], TUTORING_TIMES[j], office))
    availabilitiesBySlot = {}
    for slot in slots:
        availabilitiesBySlot[slot] = avails
    slotsByPerson = NiceDict(2)
    
    run_test(16, 1, availabilitiesBySlot, slotsByPerson)
    
    
    print "test 3: eight slots, four people, all available"
    
    avails = [("personA", 0.5), ("personB", 0.5), ("personC", 0.5), ("personD", 0.5)]
    slots = []
    for i in range(2):
        for office in (SODA, CORY):
            for j in range(2):
                slots.append(Slot(TUTORING_DAYS[i], TUTORING_TIMES[j], office))
    availabilitiesBySlot = {}
    for slot in slots:
        availabilitiesBySlot[slot] = avails
    slotsByPerson = NiceDict(2)
    
    run_test(32, 1, availabilitiesBySlot, slotsByPerson)
    
    print "test 4: eight slots, four people, all available, differing preferences, few\
        solutions, nontrivial"
    
    availsCory = "A1p B1p C1p D2, A1p B2p C1p D1\n"
    availsCory +="A1p B2p C2p D2, A2p B1p C1p D1"
    
    availsSoda = "A1 B1p C1 D2p, A1 B2p C1 D1p\n"
    availsSoda +="A1 B2p C2 D2p, A2 B1p C1 D1p"
    availabilitiesBySlot = parse_into_availabilities_by_slot(availsCory, availsSoda)
    
    slotsByPerson = NiceDict(2)
    
    run_test(38, 1, availabilitiesBySlot, slotsByPerson)
    
    print "passed %d of %d tests" % (PASSED[0], PASSED[0]+ FAILED[0])
#!python
#holds methods used to calculate a schedule given preference and scoring information

import heapq, random, sys, time, thread

try:
    from hkn.tutor.constants import *
except:
    try:
        from parameters import CORY, SODA, TUTORING_DAYS, TUTORING_TIMES,\
SCORE_CORRECT_OFFICE, SCORE_MISS_PENALTY, SCORE_PREFERENCE, SCORE_ADJACENT,\
SCORE_ADJACENT_SAME_OFFICE, DEFAULT_HOURS
        print "read from parameters.py"
    except:
        raise "cannot find neither hkn.tutor.constants nor parameters"
try:
    from hkn.utils import NiceDict
except:
    class NiceDict(dict):
        def __init__(self, defaultValue = False, *a, **kw):
            self.defaultValue = defaultValue
            dict.__init__(self, *a, **kw)
        
        """
        reverses a NiceDict so that values map to keys, does not gracefully handle
        non-unique values
        """
        def invertedCopy(self):
            ret = NiceDict(self.defaultValue)
            for key in self:
                if self[key] in ret:
                    raise 'Duplicate value "' + self[key] + '", cannot invert!'
                ret[self[key]] = key
            return ret
        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)
        
        def __missing__(self, key):
            return self.defaultValue
        
        def copy(self):
            return self.__copy__(self)
        
        def __copy__(self):
            return type(self)(self.defaultValue, self)
        
        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.defaultValue,
                              copy.deepcopy(self.items()))
        def __repr__(self):
            return 'NiceDict(%s, %s)' % (self.defaultValue,
                                            dict.__repr__(self))


#used for reading characters from input
charHolder = ['']
signalHolder = [True, True]
#readlock = thread.allocate_lock()
inputReader = [None]


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

totalTimes = {}
totalCalls = {}
maxTimes = {}

def track_timing(func):
    """
    used to track how much time is spent on each method
    """
    def wrapper(*arg, **kwargs):
        t1 = time.time()
        res = func(*arg, **kwargs)
        t2 = time.time()
        funcName = func.func_name
        if funcName not in totalTimes:
            totalTimes[funcName] = 0.0
            totalCalls[funcName] = 0.0
            maxTimes[funcName] = 0.0
        totalTimes[funcName] += (t2-t1)*1000.0
        totalCalls[funcName] += 1.0
        maxTimes[funcName] = max(maxTimes[funcName], (t2 - t1) * 1000.0)
        return res
    return wrapper

def clear_timing():
    for key in totalTimes.keys():
        del totalTimes[key]
    for key in totalCalls.keys():
        del totalCalls[key]
    for key in maxTimes.keys():
        del maxTimes[key]
        
def print_timing():
    print "=======TIMING STATISTICS (in ms)=========="
    print "name%18.18s   %s\t%s\t\t%s\t\t%s" % ("", "average", "max", "total", "count")
    for func in totalTimes:
        print "%22.22s  %8.3f\t%8.3f\t%10.3f\t%6d" % (func, totalTimes[func] / totalCalls[func], maxTimes[func], totalTimes[func], totalCalls[func])
    print "======END TIMING STATISTICS======="


@track_timing
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


class Slot:
    def __init__(self, day, time, office):
        self.day = day
        self.time = time
        self.office = office
    
    def __hash__(self):
        ret = 0
        if self.office == SODA:
            ret += 1
        return int((ret + self.day.__hash__() / 3 + self.time.__hash__() / 3))

    def __str__(self):
        return self.day + ' ' + self.time + ' ' + self.office
    
    def __repr__(self):
        return "Slot<%s %s %s>" % (self.day, self.time, self.office)
    
    def __eq__(self, other):
        otherstuff = dir(other)
        return 'day' in otherstuff and 'time' in otherstuff and 'office' in otherstuff and \
            self.day == other.day and self.time == other.time and self.office == other.office
    
    def other_office_slot(self):
        if self.office == CORY:
            otherOffice = SODA
        else:
            otherOffice = CORY
        return Slot(self.day, self.time, otherOffice)
    
    def earlier_slot(self):
        """
        returns the slot one hour earlier, same office and day
        Returns None if this is the earliest slot
        """
        earlierTime = None
        for time in TUTORING_TIMES:
            if time == self.time:
                break
            earlierTime = time
        if earlierTime == None:
            return None
        return Slot(self.day,earlierTime, self.office)
    
    def all_adjacent_slots(self):
        """
        returns all slots that are within one hour, regardless of office
        """
        earlierTime = None
        laterTime = None
        last_iter = False
        for time in TUTORING_TIMES:
            if last_iter:
                laterTime = time
                break
            if time == self.time:
                last_iter = True
            else:
                earlierTime = time
        ret = []
        for time in (earlierTime, laterTime):
            if time != None:
                slot = Slot(self.day, time, self.office)
                ret.append(slot)
                ret.append(slot.other_office_slot())
        
        return ret
    
class State(dict):
    """
    Simply a dictionary with an instance variable "meta" that can be used for storing
    useful metadata about this state.  noneCount and meta is copied (maybe shallow) when
    State is copied
    
    States may be compared, in which case they are compared by estCost()
    
    States may be hashed (unlike dictionaries)
    
    also has make_child, estCost, isGoal, initialize_keys, and pretty_print methods
    
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
        self.hashValue = False
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
    
    def make_child(self, slot, person):
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
        if self.hashValue:
            raise "cannot modify state after calling it's hash funciton"
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
    
    def is_adjacent(self, other, adjacency_checker = are_adjacent_hours):
        return adjacency_checker(self, other)
        
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
    
    @track_timing
    def __hash__(self):
        if self.hashValue:
            return self.hashValue
        ret = 0
        for key in self:
            ret += key.__hash__() % 3000 * str(self[key]).__hash__() % 3000
        self.hashValue = ret
        return self.hashValue
    
    def pretty_print(self):
        """
        prints this state in a nice to read fashion.  Be careful if editing this method,
        since it must still be parsable by parse_into_states
        """
        ret = "----------\n"
        
        if 'cost' in self.meta:
            ret += 'cost: ' + str(self.meta['cost'])
            ret += ', heuristic: ' + str(self.meta['heuristic'])
            ret += '\n'
        
        for office in (CORY, SODA):
            ret += office
            for day in TUTORING_DAYS:
                ret += "\t" + day[0:3]
            ret += '\n'
            for time in TUTORING_TIMES:
                ret += time
                for day in TUTORING_DAYS:
                    slot = Slot(day, time, office)
                    if slot in self:
                        ret += "\t" + str(self[slot])
                    else:
                        ret += "\t"
                ret += "\n"
        ret += "----------\n"
        return ret
    
    def parse_into_states(data):
        """
        parse a string of pretty printed states back into a list of states.  Returned states
        will always have string values.
        """
        ret = []
        for stateString in data.split('----------\n'):
            if stateString == '':
                continue
            try:
                stateStringLines = stateString.split('\n')
                state = State()
                
                #read cost and heuristic info
                state.meta['cost'] = int(stateStringLines[0].split(',')[0][5:])
                state.meta['heuristic'] = int(stateStringLines[0].split(',')[1][11:])
                
                #drop the cost line
                stateStringLines = stateStringLines[1:]
                for office in (CORY, SODA):
                    #drop the line describing the office / days
                    stateStringLines = stateStringLines[1:]
                    for time in TUTORING_TIMES:
                        timeAssignments = stateStringLines[0].split('\t')
                        timeAssignments = timeAssignments[1:] #drop the time from the front
                        for day in TUTORING_DAYS:
                            if timeAssignments[0] != '':
                                state[Slot(day, time, office)] = timeAssignments[0].strip()
                            timeAssignments = timeAssignments[1:] #done processing this assignment
                        stateStringLines = stateStringLines[1:] #done processing this line
                
                ret.append(state)
            except:
                #do nothing, don't add this one to the list
                raise
        return ret
    parse_into_states = staticmethod(parse_into_states)
    
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
    
    All states in visited have both 'cost' and 'heuristic' in their meta information
    and have been pushed to the priority queue.
    
    All states pushed into StateTracker are keys in visited.  Visited states
    evaluate to true in visited[state][1].  The key is stored in visited[state][0]
    
    All states generated by filteredSuccessors are placed as keys into visited.
    """
    def __init__(self,
                 maximumCost=330,
                 get_successors=lambda state:[],
                 heuristic=lambda state, stateTracker=False: 0,
                 get_cost=lambda state, slot, person:1):
        self.priorityQueue = PriorityQueue()
        self.secondaryPriorityQueue = PriorityQueue() #stores states with costs over maximumCost
        
        self.visited = NiceDict(["key",False])
        
        self.maximumCost = maximumCost
        self.get_successors = get_successors
        self.heuristic = lambda state: heuristic(state, stateTracker = self)
        self.get_cost = get_cost
        
        self.stats = {'pushed':0,
                      'popped':0,
                      'visited':0,
                      'backtracks':0,
                      'successors':0}
    
    @track_timing
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
    
    @track_timing
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
                    #replace s with the one in visited, which already has cost calculated
                    s = visitedInfo[0]
#                    if 'heuristic' not in s.meta:
#                        #calculate heuristic
#                        s.meta['heuristic'] = self.heuristic(s)
#                        self.push(s)
                else:
                    #calculate cost.  All states with cost are in visited, and all states in visited
                    #have costs.  This is not in visited.
                    s.meta['cost'] = state.meta['cost'] + self.get_cost(state,
                                                                        s.meta['slotAssigned'],
                                                                        s.meta['personAssigned'])
                    s.meta['heuristic'] = self.heuristic(s)
                    
                    #store this state
                    if s.meta['heuristic']:
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
    
    @track_timing
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
    
    @track_timing
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
    
    @track_timing
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

@track_timing
def generate_schedule(availabilitiesBySlot = NiceDict([]),
                      adjacency_checker = are_adjacent_hours,
                      slotsByPerson = False, #need to provide this
                      scoring = {"correct_office":SCORE_CORRECT_OFFICE,
                                 "miss_penalty":SCORE_MISS_PENALTY,
                                 "adjacent":SCORE_ADJACENT,
                                 "adjacent_same_office":SCORE_ADJACENT_SAME_OFFICE,
                                 "preference":SCORE_PREFERENCE},
                      options = NiceDict(False,
                                         {"random_seed":False,
                                          "machineNum":False,
                                          "maximumCost":False
                                          })
                      ):
    """
    Returns:
        list of best states found, from best to worst.
    Arguments:
        availabilitiesBySlot: Dictionary from slot to list of "preference details"
        slotsByPerson: Dictionary from person to number of slots that person should be
            assigned.  Must be provided.
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
            machineNum: if multiple machines are executing, assign each a integer increasing from 0
            maximumCost: ignore states with costs higher than this
    """
    if not options['random_seed']:
        random.seed() #uses system time or an operating system's source of randomness
    else:
        random.seed(randomSeed)

    #generosity is the disposition to choose a nongreedy successor, which goes down over time
    #because it's the opposite of greediness! -rzheng
    generosity = options['machineNum'] or 0
    
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
    
    my_heuristic = lambda state, stateTracker=False: heuristic(state=state,
                                                       costs=costs,
                                                       availabilitiesBySlot=availabilitiesBySlot,
                                                       stateTracker=stateTracker)
    
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
    
    
    stateTracker = StateTracker(
                        get_successors = my_get_successors,
                        heuristic=my_heuristic,
                        get_cost=my_get_cost)
    
    state = options['initialState']
    if not state:
        state = State().initialize_keys(availabilitiesBySlot)
        state.meta['parent'] = None
        state.meta['cost'] = 0
        state.meta['heuristic'] = my_heuristic(state, stateTracker=stateTracker)
    
    if options['maximumCost'] and options['maximumCost'] > 0:
        stateTracker.increaseMaximumCostTo(options['maximumCost'])
    stateTracker.push(state)
    
    iterations = 0
    maxIterations = 10**3 #TODO change!
    feedbackPeriod = 250 #number of iterations to go between printing stuff to user
    currentMaxIterations = maxIterations
    bestSoFar = []
    goalsFound = 0
    maxKept = 100
    bestCost = 0
    startTime = time.time()
    oldTime = startTime
    lastGoalTime = 0.0
    #create thread to handle user input if one not in use
    if inputReader[0] == None:
        print "creating new input reader"
        inputReader[0] = thread.start_new_thread(read_one_char_into_buffer, ())
    else:
        #reset reader data
        print "resetting input reader, lock state is %s" % 'disabled'#readlock.locked()
        charHolder[0] = ''
        signalHolder[0] = True
        signalHolder[1] = True
    try:
        while state != None:
            if True:#readlock.acquire(0): #only acquire if can do so without waiting
                char = charHolder[0]
                if len(char) > 0:
                    if char == 'x':
                        print "halting execution"
#                        readlock.release()
                        break
                    elif char == 'p':
                        print "dumping to schedulerDump.txt"
                        #open file and dump
                        dumpFile = open('schedulerDump.txt', 'w')
                        dumpFile.write("Created at iteration " + str(iterations) + '\n\n')
                        for e in bestSoFar:
                            dumpFile.write(e.pretty_print() + '\n\n')
                        dumpFile.close()
                    elif char == 'c':
                        print "continuing execution"
                        currentMaxIterations = iterations + maxIterations
                    charHolder[0] = ''
                    signalHolder[1] = True #signal to start reading characters again
#                readlock.release()
            if iterations % feedbackPeriod == 0:
                newTime = time.time()
                if iterations >= currentMaxIterations:
                    print '===================================='
                    print 'Completed %d iterations. in %d seconds' % (iterations,
                                                                      newTime - startTime)
                    print 'Found %d goals.  Best goal\'s cost:%d' % (goalsFound,
                                                                     bestCost)
                    print "Last %d iterations took %d seconds" % (feedbackPeriod,
                                                                      (newTime - oldTime))
                    print "Last goal found %d seconds ago" % (newTime - lastGoalTime)
                    print ''
                    print "Press 'x' and Enter to halt execution and return the best so far"
                    print "Press 'p' and Enter to print the best solutions to schedulerDump.txt"
                    print "Press 'c' and Enter to continue execution and suppress this message \
for %d iterations" % maxIterations
                    print '===================================='
                else:
                    print "\titeration: %d, best goal of %d: %d" % (iterations,
                                                                    goalsFound,
                                                                    bestCost)
                    print "Last %d iterations took %d seconds" % (feedbackPeriod,
                                                                  (newTime - oldTime))
            oldTime = newTime
    #            print "\tstats: %s" % stateTracker.stats
    #            print "\tstate: %s" % dict(state)
            iterations += 1
            stateTracker.visit(state)
            
            if state.isGoal():
                tmp = state.copy()
                tmp.meta['parent'] = 'removed'
    #            print "\tfound goal: %s" % tmp
                
                goalsFound += 1
                lastGoalTime = time.time()
                
                #no successors, this is a goal state.  Try to find a better one by hill climbing
                state = my_hill_climb(state)
                
                #tell stateTracker about this state and the new max cost
                stateTracker.push(state)
                stateTracker.visit(state)
                stateTracker.maximumCost = state.estCost()
                bestCost = state.estCost()
                
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
                    if generosity > 0:
                        successors.sort()
                        state = successors[generosity % len(successors)]
                        generosity = generosity / len(successors)
                    else:
                        state = min(successors)
                
        print "\tstateTracker stats: %s" % str(stateTracker.stats)
        print "\tfound %d goals in %d iterations" % (goalsFound, iterations)
        bestCosts = "best goals had costs: ["
        for goal in bestSoFar:
            bestCosts += str(goal.meta['cost']) + ","
        print bestCosts[:-1] + ']'
    except:
        signalHolder[0] = False #be sure to stop the other thread
        raise
    
    signalHolder[0] = False #be sure to stop the other thread
    return bestSoFar

@track_timing
def get_successors(state=State(),
                   availabilitiesBySlot=NiceDict([]),
                   slotsByPerson=False):
    """
    Returns: list of states that are successsors to the given state, or empty list if none.
    Each state will have 'parent', 'slotAssigned', and 'personAssigned', but missing
    'cost' and 'heuristic' info in the meta
    
    slotAssigned and personAssigned are the slot / person assigned when coming from parent
    
    INCOMPLETE - this is a "correct" but slightly dumb version
    
    Algorithm notes:
    
    Finds slot with fewest remaining availabilities and generates successors from who can
    still fill that slot
    
    Does not consider people who can only fill a few slots
    """
    ret = []
    emptySlots = []
    numAssigned = NiceDict(0)
    for slot in state:
#        print "considering slot" + str(slot)
        person = state[slot]
        if person == None:
            #keep track of this empty spot for later
            emptySlots.append(slot)
        else:
            #note that this person has been assigned
            if person not in numAssigned:
                numAssigned[person] = 1
            else:
                numAssigned[person] += 1
    
    #numAssigned is now correct
    
    availsInEmptySlot = []
    numAvailsInEmptySlot = 10000 #much larger than anything possible
    for slot in emptySlots:
        people = []
        numPeople = 0
        other_office_slot = slot.other_office_slot()
        for person in [detail[0] for detail in availabilitiesBySlot[slot]]:
#                print 'considering person: ' + person
            if numAssigned[person] >= slotsByPerson[person] or state[other_office_slot] == person:
                #person cannot tutor more, or is tutoring this time in another office
#                    print 'skipping person who is full or tutoring in other office'
                continue
            people.append(person)
            numPeople += 1
        
        #see if this is fewer than previously seen
        if numPeople < numAvailsInEmptySlot:
#                print "considering slot with availabilities for: " + str(people)
            #consider this slot as a candidate for generating fewest successors
            emptySlot = slot
            availsInEmptySlot = people
            numAvailsInEmptySlot = numPeople
    
    for person in availsInEmptySlot:
        successor = state.make_child(emptySlot, person)
        ret.append(successor)
    
    if len(ret) > 0:
        for e in ret:
            if state.noneCount <= e.noneCount:
                raise "successor does not have more assignments than parent"
    
    return ret

@track_timing
def heuristic(state=State(),
              costs=NiceDict(0, {'base':1}),
              availabilitiesBySlot = NiceDict([]),
              adjacency_checker = are_adjacent_hours,
              slotsByPerson = False,
              stateTracker = StateTracker()):
    """
    Returns: integer estimate of optimal future costs from this state
             if unsolvable, return False
    Arguments:
        state - dictionary from slots to assignments, None for none assigned
        costs - see documentation at top
        availabilitiesBySlot - see documentation for generateSchedule
        slotsByPerson - dictionary from person to total # slots to be assigned
        stateTracker - provide to allow memoization of costs
        
    Not a very smart heuristic right now.  Handles adjacencies poorly, puts
    most optimistic person in each slot according to get_cost
    """
    ret = 0
    
    def my_get_cost(state, slot, person):
        """
        was, memoized get cost using stateTracker, but that turned out to be slower
        """
#        newState = state.make_child(slot, person)
#        if newState in stateTracker.visited:
#            #replace newState with the correct instance of newState
#            newState = stateTracker.visited[newState][0]
#            if 'cost' in newState:
#                return stateTracker.visited[newState][0].meta['cost'] - state.meta['cost']
#            #need to calculate cost
#        else:
#            stateTracker.visited[newState] = [newState, False]
        temp = get_cost(initialState=state,
                        slot=slot,
                        person=person,
                        costs=costs,
                        adjacency_checker=adjacency_checker,
                        availabilitiesBySlot=availabilitiesBySlot)
#        newState.meta['cost'] = state.meta['cost'] + temp
        return temp
    
    
    for slot in state:
        if state[slot] == None:
            avails = availabilitiesBySlot[slot]
            if len(avails) == 0:
                return False #this is an unsolvable state
            ret += min([my_get_cost(state, slot, detail[0]) for detail in avails])
            
            #assume that we could have filled an empty earlier slot for the same person
            #only count earlier slots, so we don't double count (as badly)
            earlier_slot = slot.earlier_slot()
            if earlier_slot != None:
                if state[earlier_slot] == None:
                    ret -= costs['adjacent_same_office']
                elif state[earlier_slot.other_office_slot()] == None:
                    ret -= costs['adjacent']
    return ret

@track_timing
def hill_climb(initialState=State(),
              costs=NiceDict(0, {'base':1}),
              slotsByPerson=False,
              adjacency_checker=are_adjacent_hours,
              availabilitiesBySlot=NiceDict([])):
    """
    Returns: best state found, with cost info in the meta.  If did any hill climbing,
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
    
#    Returns a new state with the three specified entries swapped
#    Swaps person in slot one to slot two, slot two to slot three, and slot three to slot one
    def three_swap_state(state, slotOne, slotTwo, slotThree):
        newState = State(state)
        newState[slotOne] = state[slotThree]
        newState[slotTwo] = state[slotOne]
        newState[slotThree] = state[slotTwo]
        return newState
    
#    Begin Hillclimbing
#    Currently, the hill climber only keeps track one state.
#    We could have beam search by tracking more states in potentialStatesAndCosts.
    betterStates = 0
    worseStates = 0
    bestStateAndCost = (State(initialState), 0)
    bestDiffs = []
    potentialStatesAndCosts = [bestStateAndCost]
    while len(potentialStatesAndCosts) > 0:
        print "climbing hill"
        state, cost = potentialStatesAndCosts.pop(0)
        for slotOne in state:
            for slotTwo in state:
                if slotTwo <= slotOne or slotOne.time == slotTwo.time:
                    continue
                for slotThree in state:
                    if slotThree <= slotTwo or slotTwo.time == slotThree.time or slotOne.time == slotThree.time:
                        continue
                    personOne = state[slotOne]
                    personTwo = state[slotTwo]
                    personThree = state[slotThree]
                    personOneToSlotTwo = False
                    personOneToSlotThree = False
                    personTwoToSlotOne = False
                    personTwoToSlotThree = False
                    personThreeToSlotOne = False
                    personThreeToSlotTwo = False
                    for person in [detail[0] for detail in availabilitiesBySlot[slotOne]]:
                        personThreeToSlotOne = personThreeToSlotOne | (person==personThree)
                        personTwoToSlotOne = personTwoToSlotOne | (person==personTwo)
                    for person in [detail[0] for detail in availabilitiesBySlot[slotTwo]]:
                        personOneToSlotTwo = personOneToSlotTwo | (person==personOne)
                        personThreeToSlotTwo = personThreeToSlotTwo | (person==personThree)
                    for person in [detail[0] for detail in availabilitiesBySlot[slotThree]]:
                        personTwoToSlotThree = personTwoToSlotThree | (person==personTwo)
                        personOneToSlotThree = personOneToSlotThree | (person==personOne)
                    
                    if personOneToSlotTwo and personTwoToSlotThree and personThreeToSlotOne:
                        newState = three_swap_state(state, slotOne, slotTwo, slotThree)
                        newState.meta['swap'] = "%s -> %s -> %s" % (slotOne , slotTwo , slotThree)
                        costDiff = my_get_cost_difference(state, newState)
                        if costDiff < 0:
                            betterStates += 1
                            newCost = cost + costDiff
                            newStateAndCost = (newState, newCost)
                            if newCost < bestStateAndCost[1]:
                                bestStateAndCost = newStateAndCost
                                potentialStatesAndCosts = [(newStateAndCost)]
                        else:
                            worseStates += 1
                    
                    if personOneToSlotThree and personTwoToSlotOne and personThreeToSlotTwo:
                        newState = three_swap_state(state, slotOne, slotThree, slotTwo)
                        newState.meta['swap'] = "%s -> %s -> %s" % (slotThree , slotTwo , slotOne)
                        costDiff = my_get_cost_difference(state, newState)
                        if costDiff < 0:
                            betterStates += 1
                            newCost = cost + costDiff
                            newStateAndCost = (newState, newCost)
                            if newCost < bestStateAndCost[1]:
                                bestStateAndCost = newStateAndCost
                                potentialStatesAndCosts = [(newStateAndCost)]
                        else:
                            worseStates += 1
        print "cost delta = ", bestStateAndCost[1]
        print bestStateAndCost[0].meta['swap']
    
    print 'HillClimb Stats'
    print 'Number of Better States = ', betterStates
    print 'Number of Worse States = ', worseStates, '\n'
    bestState, bestCost = bestStateAndCost
    bestState.meta['cost'] = initialState.meta['cost'] + bestCost
    bestState.meta['heuristic'] = 0
    return bestState




#helpful methods below
@track_timing
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
    
    cost = costs['base']
    if adjacency_checker == are_adjacent_hours:
        #safe to use all_adjacent_slots
        slots = [s for s in slot.all_adjacent_slots() if s in initialState]
        #don't need to execute code to know they're adjacent, so use dummy function
        my_adjacency_checker = lambda x, y: True
    else:
        slots = initialState
        my_adjacency_checker = adjacency_checker
    for key in slots:
        if key != slot and initialState[key] == person and my_adjacency_checker(key, slot):
            if key.office == slot.office:
                cost -= costs['adjacent_same_office']
            else:
                cost -= costs['adjacent']
    found = False
    for detail in availabilitiesBySlot[slot]:
        if detail[0] == person:
            cost -= costs['preference'][detail[1]]
            found = True
            break
    
    
    return cost

@track_timing
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
        commonAncestor = State()
        for key in oldState:
            oldPerson = oldState[key]
            if newState[key] == oldPerson:
                commonAncestor[key] = oldPerson
            else:
                commonAncestor[key] = None
    
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

@track_timing
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

def read_one_char_into_buffer():
    """
    does not put any "space" onto buffer.  Meant to be called in a thread.  Exits when it sees
    an 'x'
    """
    stdin = sys.stdin #std in file descriptor
    temp = ''
    while True:
#        readlock.acquire()
        keep_running = signalHolder[0]
#        readlock.release()
        if not keep_running:
            break
        
        while True:
#            readlock.acquire()
            readyToReceive = signalHolder[1]
#            readlock.release()
            if not readyToReceive:
                break
            
            temp = stdin.read(1)
            if len(temp) > 0 and not temp.isspace():
#                readlock.acquire()
                signalHolder[1] = False #rest until signalled to read another character
                charHolder[0] = temp[0]
                print "placed character into charHolder: %s (may have to try many times)" % temp[0].__repr__()
#                readlock.release()
                
                if temp == 'x':
                    print "reader exiting"
#                    readlock.acquire()
                    signalHolder[0] = False
                    signalHolder[1] = False
                    inputReader[0] = None
#                    readlock.release()
                    return

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
         Slot<Tuesday 12-1 Cory>: [(A, 1.5), (B, 0.5), (C, 0.5), (D, 1)],
        }
    """
    ret = {}
    office = CORY
    for timesString in (coryTimes, sodaTimes):
        hourIndex = 0
        for hourAvailString in timesString.split('\n'):
            dayIndex = 0
            for dayAvailString in hourAvailString.split(','):
                for detailString in dayAvailString.split(' '):
                    if detailString == '':
                        continue
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

def random_availabilities_by_slot():
    """
    Returns an availabilitiesBySlot object with random availabilities and preferences.
    May not be solvable.
    
    Written by Ryan Zheng, edited by Darren Lo to work as a function
    """
    retry = True
    while(retry):
        retry = False
        cory = []
        soda = []
        both = []
        counts = {}
        
        for i in range(10):
            for list, ch in zip((cory, soda, both), ('c', 's', 'b')):
                list.append(chr(65+i) + ch)
        
        corystr = ''
        sodastr = ''
        for j in range(6):
            for i in range(5):
                for c in cory:
                    if(random.random() < .4):
                        if c not in counts:
                            counts[c] = 0
                        counts[c] += 1
                        pref = str(int(random.random() * 2) + 1)
                        corystr += c + pref + "p "
                        sodastr += c + pref + " "
                for c in soda:
                    if(random.random() < .4):
                        if c not in counts:
                            counts[c] = 0
                        counts[c] += 1
                        pref = str(int(random.random() * 2) + 1)
                        corystr += c + pref + " "
                        sodastr += c + pref + "p "
                for c in both:
                    if(random.random() < .4):
                        if c not in counts:
                            counts[c] = 0
                        counts[c] += 1
                        pref = str(int(random.random() * 2) + 1)
                        corystr += c + pref + "p "
                        sodastr += c + pref + "p "
        
                if i != 4:
                    corystr += ", "
                    sodastr += ", "
                else:
                    corystr += "\n"
                    sodastr += "\n"
        
        for c in counts:
            if counts[c] < 2:
                retry = True
                #can't solve because somebody has fewer than 2 availabilities
    
    #construct dictionary
    return parse_into_availabilities_by_slot(corystr, sodastr)

def generate_from_random(destFileName = "randomSchedulerOutput.txt"):
    clear_timing()
    ret = generate_schedule(availabilitiesBySlot=random_availabilities_by_slot(),
                            slotsByPerson=NiceDict(2),
                            options=NiceDict(False))
    print_timing()
    dump = open(destFileName, 'w+') #truncates file if it exists
    for state in ret:
        s = state.pretty_print()
        print s
        dump.write(s)
    
    print "wrote output to %s" % destFileName
    
def generate_from_file(destFileName = "schedulerOutput.txt", options=NiceDict(False)):
    try:
        from parameters import coryTimes, sodaTimes, defaultHours, exceptions, scoring
        from parameters import options as poptions
    except:
        print "Could not find valid file 'parameters.py'"
        return
    for key in poptions:
        if key in options:
            poptions[key] = options[key]
    clear_timing()
    ret = generate_schedule(availabilitiesBySlot=parse_into_availabilities_by_slot(coryTimes,
                                                                                   sodaTimes),
                            slotsByPerson=NiceDict(defaultHours, exceptions),
                            scoring=scoring,
                            options=NiceDict(False, poptions))
    print_timing()
    dump = open(destFileName, 'w+') #truncates file if it exists
    for state in ret:
        s = state.pretty_print()
        print s
        dump.write(s)
    
    print "wrote output to %s" % destFileName
    

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
                return ret
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        print "failed test, expected %s\n\t but got %s\n" % (expected, ret)
        FAILED[0] += 1
        return ret
    
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
                return ret
        except:
            print "Unexpected error:", sys.exc_info()
            raise
        print "failed test, expected maxCost %s minLength %s\n\t but got %s\n" % (maxCost, minLength, ret)
        FAILED[0] += 1
        return ret
    
    print "Running tests on scheduler..."
    
    
    print "test 1: two slots, two people, each only 1 availability"
    
    availabilitiesBySlot = parse_into_availabilities_by_slot("A1p", "B1p")
    
    slotsByPerson = NiceDict(1)
    expected = [State({Slot(TUTORING_DAYS[0], TUTORING_TIMES[0], CORY):'A',
                       Slot(TUTORING_DAYS[0], TUTORING_TIMES[0], SODA):'B'})]
    
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
    
    clear_timing()
    run_test(32, 1, availabilitiesBySlot, slotsByPerson)
    print_timing()
    
    print "test 4: eight slots, four people, all available, differing preferences, few\
        solutions, nontrivial"
    
    availsCory = "A1p B1p C1p D2, A1p B2p C1p D1\n"
    availsCory +="A1p B2p C2p D2, A2p B1p C1p D1"
    
    availsSoda = "A1 B1p C1 D2p, A1 B2p C1 D1p\n"
    availsSoda +="A1 B2p C2 D2p, A2 B1p C1 D1p"
    availabilitiesBySlot = parse_into_availabilities_by_slot(availsCory, availsSoda)
    
    slotsByPerson = NiceDict(2)
    
    run_test(38, 1, availabilitiesBySlot, slotsByPerson)
    
    
    print "test 5: eight slots, three people, gaps and preferences in availabilities"
    
    availsCory = "A1p B1p C1p, A1p B2p C1p\n"
    availsCory +="A2p     C2p, A2p B1p C1p"
    
    availsSoda = "A1 B1p C1, A1 B2p C1\n"
    availsSoda +="A2     C2, A2 B1p C1"
    availabilitiesBySlot = parse_into_availabilities_by_slot(availsCory, availsSoda)
    
    slotsByPerson = NiceDict(2, {'A':3, 'B':3})

    """
    expected optimal schedule:
    Cory  M    T
    11    A1p  A1p
    12    A2p  C1p
    
    Soda  M    T
    11    B1p  B2p
    12    C2   B1p
    
    cost of 56
    """
    
    results = run_test(56, 1, availabilitiesBySlot, slotsByPerson)
#    schedules = ""
#    for r in results:
#        schedules += r.pretty_print() + '\n\n'
#    print "found schedules: \n" + schedules

    print "test 6: 60 slots, only 1 optimal schedule, 4^30 possible ones"
    
    availsCory = "Ac1p As1, Dc1p Ds1, Gc1p Gs1, Jc1p Js1, Mc1p Ms1\n"
    availsCory +="Ac1p As1, Dc1p Ds1, Gc1p Gs1, Jc1p Js1, Mc1p Ms1\n"
    availsCory +="Bc1p Bs1, Ec1p Es1, Hc1p Hs1, Kc1p Ks1, Nc1p Ns1\n"
    availsCory +="Bc1p Bs1, Ec1p Es1, Hc1p Hs1, Kc1p Ks1, Nc1p Ns1\n"
    availsCory +="Cc1p Cs1, Fc1p Fs1, Ic1p Is1, Lc1p Ls1, Oc1p Os1\n"
    availsCory +="Cc1p Cs1, Fc1p Fs1, Ic1p Is1, Lc1p Ls1, Oc1p Os1\n"
    
    availsSoda = "As1p Ac1, Ds1p Dc1, Gs1p Gc1, Js1p Jc1, Ms1p Mc1\n"
    availsSoda +="As1p Ac1, Ds1p Dc1, Gs1p Gc1, Js1p Jc1, Ms1p Mc1\n"
    availsSoda +="Bs1p Bc1, Es1p Ec1, Hs1p Hc1, Ks1p Kc1, Ns1p Nc1\n"
    availsSoda +="Bs1p Bc1, Es1p Ec1, Hs1p Hc1, Ks1p Kc1, Ns1p Nc1\n"
    availsSoda +="Cs1p Cc1, Fs1p Fc1, Is1p Ic1, Ls1p Lc1, Os1p Oc1\n"
    availsSoda +="Cs1p Cc1, Fs1p Fc1, Is1p Ic1, Ls1p Lc1, Os1p Oc1\n"
    
    availabilitiesBySlot = parse_into_availabilities_by_slot(availsCory, availsSoda)
    
    slotsByPerson = NiceDict(2)
    clear_timing()
    results = run_test(240, 1, availabilitiesBySlot, slotsByPerson)
    print_timing()
    schedules = ""
    for r in results[:3]:
        schedules += r.pretty_print() + '\n\n'
    print "found schedules: \n" + schedules
    
    print "passed %d of %d tests" % (PASSED[0], PASSED[0]+ FAILED[0])
    
def test_heuristic():
    print "testing heuristic"
    
    costs = {'base': max(SCORE_ADJACENT, SCORE_ADJACENT_SAME_OFFICE) * 2 +
                 max(SCORE_PREFERENCE.values()) +
                 SCORE_CORRECT_OFFICE +
                 1,
         'adjacent': SCORE_ADJACENT,
         'adjacent_same_office': SCORE_ADJACENT_SAME_OFFICE}
    costs['preference'] = {}
    for int_key in SCORE_PREFERENCE:
        costs['preference'][int_key] = SCORE_PREFERENCE[int_key]
        costs['preference'][int_key - 0.5] = SCORE_PREFERENCE[int_key] + SCORE_CORRECT_OFFICE
    
    s = State()
    
    availsCory = "A1p B1p\n"
    availsCory +="A1p B2p"
    
    availsSoda = "A1p B1\n"
    availsSoda +="A1p B2"
    availabilitiesBySlot = parse_into_availabilities_by_slot(availsCory, availsSoda)
    
    s.initialize_keys(availabilitiesBySlot)
    
    slotsByPerson = NiceDict(2)
    
    expected = 4 * (costs['base'] - costs['preference'][0.5]) - 2 * costs['adjacent_same_office']
    result = heuristic(s, costs, availabilitiesBySlot, slotsByPerson = slotsByPerson)
    if expected == result:
        print "start heuristic is correct"
    else:
        print "expected %d, start state heuristic: %d" % (expected, result)
    
def hill_climb_test():
    from parameters import coryTimes, sodaTimes
    str = "----------\n\
cost: 351, heuristic: 0\n\
Cory	Mon	Tue	Wed	Thu	Fri\n\
11a-12	52WayneF	54YasinA	360SandyW	364JerryZ	23IngridL\n\
12-1	36MichaelT	54YasinA	322KeatonM	30JudyH	215VishayN\n\
1-2	46ShervinJ	190NirA	35MatthewE	36MichaelT	365RyanZ\n\
2-3	46ShervinJ	11BrianK	35MatthewE	183JohnnyT	215VishayN\n\
3-4	52WayneF	6AngelaH	335MichelleA	25JarodP	365RyanZ\n\
4-5	48SurajG	6AngelaH	333MinX	25JarodP	217SuhaasP\n\
Soda	Mon	Tue	Wed	Thu	Fri\n\
11a-12	360SandyW	224HishamZ	319DarrenL	183JohnnyT	48SurajG\n\
12-1	30JudyH	39NielsJ	39NielsJ	224HishamZ	12BrianL\n\
1-2	197MichaelC	23IngridL	322KeatonM	190NirA	13BrianT\n\
2-3	197MichaelC	319DarrenL	24JamesL	364JerryZ	217SuhaasP\n\
3-4	335MichelleA	20GeorgeC	24JamesL	11BrianK	333MinX\n\
4-5	13BrianT	20GeorgeC	12BrianL	314ChrisL	314ChrisL\n\
----------"

    costs = {'base': max(SCORE_ADJACENT, SCORE_ADJACENT_SAME_OFFICE) * 2 +
                 max(SCORE_PREFERENCE.values()) +
                 SCORE_CORRECT_OFFICE +
                 1,
         'adjacent': SCORE_ADJACENT,
         'adjacent_same_office': SCORE_ADJACENT_SAME_OFFICE}
    costs['preference'] = {}
    for int_key in SCORE_PREFERENCE:
        costs['preference'][int_key] = SCORE_PREFERENCE[int_key]
        costs['preference'][int_key - 0.5] = SCORE_PREFERENCE[int_key] + SCORE_CORRECT_OFFICE

    availabilitiesBySlot = parse_into_availabilities_by_slot(coryTimes, sodaTimes)

    state = State.parse_into_states(str)
    newState = hill_climb(initialState=state[0], costs=costs, slotsByPerson=NiceDict(2), availabilitiesBySlot=availabilitiesBySlot)
    print newState.pretty_print()


if __name__=="__main__":
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv, "fmcr", ["file=", "machine=", "maxcost=", "randseed="])
    except getopt.GetoptError:
        print "Valid options:"
        print "  -f NAME --file=NAME    output file name"
        print "  -m NUM  --machine=NUM  machine number"
        print "  -c NUM  --maxcost=NUM  maximum cost"
        print "  -r NUM  --randseed=NUM random seed"
        sys.exit(1)
    filename = "schedulerOutput.txt"
    machineNum = False
    cost = False
    seed = False
    for opt, arg in opts:
        if opt in ('-f', '--file'):
            filename = arg
        elif opt in ('-m', '--machine'):
            machineNum = arg
        elif opt in ('-c', '--maxcost'):
            cost = arg
        elif opt in ('-r', '--randseed'):
            seed = arg

    generate_from_file(filename, options={'machineNum': machineNum, 'maximumCost': cost, 'randomSeed': seed})

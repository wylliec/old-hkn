#from hkn.enum import EnumType
from hkn.utils import NiceDict

CORY = "Cory"
SODA = "Soda"

OFFICE_CHOICES = (SODA, SODA), (CORY, CORY)

#replace below by reading from some config file
TUTORING_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
TUTORING_TIMES = ("11a-12", "12-1", "1-2", "2-3", "3-4", "4-5") #listed in order of adjacency

#lowest version number
MIN_VERSION = 1

#maximum number of courses that people can tutor per schedule
MAX_COURSES = 50

#used for scoring assignment utility, aka "happiness"
SCORE_CORRECT_OFFICE = 1
SCORE_MISS_PENALTY = 10000 #should be larger than slots * best score possible
SCORE_PREFERENCE = {1:3, 2:0} #maps from preference rank to score
SCORE_ADJACENT = 0 #not yet working

#In the future, the below contents will be managed by scripts and should NOT be managed manually
CURRENT_SEASON_NAME = "Spring" #DO NOT EDIT THIS
CURRENT_YEAR = 2008 #DO NOT EDIT THIS
#number of hours each person normally tutors
DEFAULT_HOURS = 2 #DO NOT EDIT THIS
#exceptions for people who do not tutor the default hours.  Maps from full name (first + " " + last)
#to hours
HOUR_EXCEPTIONS = NiceDict(False,{#DO NOT EDIT THIS
#BEGIN EXCEPTIONS
#END EXCEPTIONS
}) #DO NOT EDIT THIS
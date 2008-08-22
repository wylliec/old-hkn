from nice_types import NiceDict

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
SCORE_CORRECT_OFFICE = 2
SCORE_MISS_PENALTY = 10000 #should be larger than slots * best score possible
SCORE_PREFERENCE = {1:6, 2:0} #maps from preference rank to score
SCORE_ADJACENT = 1
SCORE_ADJACENT_SAME_OFFICE = 2

#In the future, the below contents will be managed by scripts and should NOT be managed manually.
#They can be edited using hkn.tutor.view.update_constants
#BEGIN AUTOMANAGED
#Current season and year now managed by semester.py
#CURRENT_SEASON_NAME = 'Spring' #DO NOT EDIT THIS
#CURRENT_YEAR = 2008 #DO NOT EDIT THIS
#number of hours each person normally tutors
DEFAULT_HOURS = 2 #DO NOT EDIT THIS
#exceptions for people who do not tutor the default hours.  Maps from person id to hours
HOUR_EXCEPTIONS = NiceDict(False,{#DO NOT EDIT THIS
#BEGIN EXCEPTIONS
48: 3,#DO NOT EDIT THIS
335: 3,#DO NOT EDIT THIS
36: 3,#DO NOT EDIT THIS
#END EXCEPTIONS
}) #DO NOT EDIT THIS
#END AUTOMANAGED

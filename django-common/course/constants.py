from nice_types import EnumType, NiceDict
from departments_constants import DEPT_ABBRS, DEPT_ABBRS_INV, DEPT_ABBRS_SET

SEMESTER_SPRING = "spring"
SEMESTER_SUMMER = "summer"
SEMESTER_FALL = "fall"

SEMESTER = EnumType(SPRING = SEMESTER_SPRING, SUMMER = SEMESTER_SUMMER, FALL = SEMESTER_FALL)
SEMESTER.add_descriptions(((SEMESTER.SPRING, "Spring"), (SEMESTER.SUMMER, "Summer"), (SEMESTER.FALL, "Fall")))

EXAMS_PREFERENCE_UNKNOWN = 0
EXAMS_PREFERENCE_NEVER_OK = 5
EXAMS_PREFERENCE_ALWAYS_ASK = 10
EXAMS_PREFERENCE_ALWAYS_OK = 15

EXAMS_PREFERENCE = EnumType(UNKNOWN = EXAMS_PREFERENCE_UNKNOWN, NEVER_OK = EXAMS_PREFERENCE_NEVER_OK, ALWAYS_ASK = EXAMS_PREFERENCE_ALWAYS_ASK, ALWAYS_OK = EXAMS_PREFERENCE_ALWAYS_OK)
EXAMS_PREFERENCE.add_descriptions(((EXAMS_PREFERENCE.UNKNOWN, "Unknown"), (EXAMS_PREFERENCE.NEVER_OK, "Never post exams"), (EXAMS_PREFERENCE.ALWAYS_ASK, "Always ask before posting exams"), (EXAMS_PREFERENCE.ALWAYS_OK, "Always OK to post exams")))

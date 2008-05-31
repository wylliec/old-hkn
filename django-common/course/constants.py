from nice_types import EnumType, NiceDict

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

#NiceDict from allcaps official department abbreviations to preferred abbreviations
DEPT_ABBR_OVERRIDE = NiceDict(False, {
    "ASTRON":  "ASTRO",
    "BIOLOGY": "BIO",
    "BIO ENG": "BIOE",
    "BUS ADM": "BA",
    "CHM ENG": "CHEME",
    "CIV ENG": "CIVE",
    "COG SCI": "COGSCI",
    "COMPSCI": "CS",
    "EL ENG":  "EE",
    "ENGIN":   "E",
    "HISTORY": "HIST", #not actually used
    "IND ENG": "IEOR",
    "INTEGBI": "IB",
    "LINGUIS": "LING", #not actually used
    "MAT SCI": "MSE",
    "MEC ENG": "ME",
    "MCELLBI": "MCB",
    "PHYSICS": "PHYS",
    "POL SCI": "POLISCI", #not actually used
    })
DEPT_ABBR_CORRECT = DEPT_ABBR_OVERRIDE.invertedCopy() #goes from preferred abbreviations to true ones

from hkn.enum import EnumType


APP_YEAR_OTHER = 0
APP_YEAR_FIRST = 1
APP_YEAR_SECOND = 2
APP_YEAR_THIRD = 3
APP_YEAR_FOURTH = 4
APP_YEAR_GRAD = 6

EECS_OPTION_I = 1
EECS_OPTION_II = 2
EECS_OPTION_III = 3
EECS_OPTION_IV = 4
EECS_OPTION_V = 5

APP_YEAR = EnumType(OTHER = APP_YEAR_OTHER, FIRST = APP_YEAR_FIRST, SECOND = APP_YEAR_SECOND, THIRD = APP_YEAR_THIRD, FOURTH = APP_YEAR_FOURTH, GRAD = APP_YEAR_GRAD)
APP_YEAR.add_descriptions(((APP_YEAR.OTHER, "Other"), (APP_YEAR.FIRST, 'First year'), (APP_YEAR.SECOND, 'Second year'), (APP_YEAR.THIRD, 'Third year'), (APP_YEAR.FOURTH, 'Fourth year'), (APP_YEAR.GRAD, 'Grad student')))

EECS_OPTION = EnumType(I = EECS_OPTION_I, II = EECS_OPTION_II, III = EECS_OPTION_III, IV = EECS_OPTION_IV, V = EECS_OPTION_V)
EECS_OPTION.add_descriptions(((EECS_OPTION.I, 'I - Electronics'), (EECS_OPTION.II, 'II - Communications, Networks and Systems'), (EECS_OPTION.III, 'III - Computer Systems'), (EECS_OPTION.IV, 'IV - Computer Science'), (EECS_OPTION.V, 'V - General')))

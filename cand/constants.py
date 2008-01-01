from hkn.constants import _const

APP = _const()
APP.YEAR = _const()
APP.OPT = _const()

APP.YEAR.FIRST = '1'
APP.YEAR.SECOND = '2'
APP.YEAR.THIRD = '3'
APP.YEAR.FOURTH = '4'
APP.YEAR.GRAD = 'G'

APP.OPT.I = 1
APP.OPT.II = 2
APP.OPT.III = 3
APP.OPT.IV = 4
APP.OPT.V = 5

APP.YEAR_CHOICES = ((APP.YEAR.FIRST, 'First year'), (APP.YEAR.SECOND, 'Second year'), (APP.YEAR.THIRD, 'Third year'), (APP.YEAR.FOURTH, 'Fourth year'), (APP.YEAR.GRAD, 'Grad student'))
APP.YEAR_CHOICES_DICT = {}
for year in APP.YEAR_CHOICES:
	APP.YEAR_CHOICES_DICT[year[0]] = year[1]

APP.OPT_CHOICES = ((APP.OPT.I, 'Electronics'), (APP.OPT.II, 'Communications, Networks and Systems'), (APP.OPT.III, 'Computer Systems'), (APP.OPT.IV, 'Computer Science'), (APP.OPT.V, 'General'))
APP.OPT_CHOICES_DICT = {}
for option in OPT_CHOICES:
	APP.OPT_CHOICES_DICT[option[0]] = option[1]

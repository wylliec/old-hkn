YEAR = "2008"
"""
The current year (used when setting klass's year attribute)
"""

TERM = ("SP", "spring")
"""
The term. First value is the appropriate query value for the berkeley online schedule, the second value is more human readable
"""

#TERM = ("SU", "summer")
#TERM = ("FL", "fall")


#DEFAULT_DEPARTMENTS = ["el eng", "compsci", "comscls", "math", "physics", "english", "history", "arabic", "engin", "civ eng", "chm eng", "pol sci"]
DEFAULT_DEPARTMENTS = ["aerosp", "ast", "astron", "bio eng", "biology", "bus adm", "chm eng", "chem", "cgb", "civ eng", "cog sci", "compsci", "econ", "el eng", "engin", "eps", "ind eng", "integbi", "mat sci", "math", "mec eng", "mcellbi", "nuc eng", "physics", "stat", "ugba"]
"""
The departments that we get scrape course & klasses for by default. The values should be the correct department abbreviation, see:
http://registrar.berkeley.edu/Scheduling/deptabb.html
"""


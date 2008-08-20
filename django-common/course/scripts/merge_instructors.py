#!/usr/bin/env python
import pickle, os
import setup_settings; setup_settings.setup(); os.chdir(setup_settings.get_cd())

from course.models import *
from course.constants import EXAMS_PREFERENCE

related_departments = [
("BIOLOGY", "MCELLBI", "IB", "BIOE", "EPS", "CHEM", "CHEME", "COGSCI"),
("PHYS", "CHEM", "BIO"),
("COMPSCI", "STAT"),
("ENGIN", "IND ENG", "EL ENG"),
("E", "ME", "MSE", "AST", "BIOE", "CIVE", "PHYS", "CHEM", "EE", "CHEME"),
("E", "IEOR", "BUS ADM", "BA"),
("E", "ME", "CIVE", "BIOE", "EE", "NUC ENG", "CHEME"),
("BUS ADM", "BA", "ECON"),
("PHYS", "ASTRO"),
("E", "EE", "CS"),
("CS", "COGSCI", "BIOE", "EE", "E"),
("EPS", "ASTRO", "MCB"),
("CS", "IEOR", "COGSCI", "PHYS"),
("POLISCI", "ECONOMICS", "HIST"),
("ECON", "MATH"),
("STAT", "BIOE"),
("MSE", "EPS"),
]

not_related_departments = [
("MCB", "CS"),
("HIST", "PHYS"),
("EPS", "CS"),
("PHYS", "ECON"),
("HIST", "EE"),
("BA", "PHYS"),
("ENGLISH", "IB"),
("ENGLISH", "EPS"),
("ME", "BA"),
("ME", "BUS ADM"),
("EE", "ASTRO"),
]

rdsets = []
for rdset in related_departments:
    rdsets.append(set([Department.get_proper_abbr(r) for r in rdset]))

nrdsets = []
for nrdset in not_related_departments:
    nrdsets.append(set([Department.get_proper_abbr(r) for r in nrdset]))

saved = []
def merge_two_instructors(instr1, instr2):
    #global saved
    #saved += (instr1.short_name(True, True), instr2.short_name(True, True))
    count = [0, 0]
    props = {}
    for prop in ("last", "first", "middle", "email"):
        prop1 = getattr(instr1, prop)
        prop2 = getattr(instr2, prop)
        if len(prop1) > len(prop2):
            props[prop] = prop1
            count[0] += 1
        elif len(prop2) > len(prop1):
            props[prop] = prop2
            count[1] += 1
        else:
            props[prop] = prop1

    winner = instr1
    loser = instr2
         
    if count[1] > count[0]:
        winner = instr2
        loser = instr1
    
    for k, v in props.items():
        setattr(winner, k, v)
    
    if loser.distinguished_teacher:
        winner.distinguished_teacher = True

    winner.save()
    
    for d in loser.departments.all():
        winner.departments.add(d)
    for k in loser.klasses.all():
        winner.klasses.add(k)
        
    loser.delete()
        
    print "Merged: Winner was %s; Loser %s" % (winner.short_name(True, True), loser.short_name(True, True))
   
    return winner
    
def exceptions(p, s):
    last = p.last
    if last in ("Hochbaum", "Whaley"):
        return True
    elif last in ("Bartlett",):
        return False
    return None
   
def prompt_candidate(p, s):

    choice = ""
    p_depts_ = set([d.abbr for d in p.departments.all()] + [p.home_department.abbr])
    s_depts_ = set([d.abbr for d in s.departments.all()] + [s.home_department.abbr])
    exc = exceptions(p, s)
    if len(p_depts_ & s_depts_) > 0:
        choice = "y"
    elif exc == True:
        choice = "y"
    elif exc == False:
        choice = "n"
    else:
        for rdset in rdsets:
            p_depts = (p_depts_ & rdset)
            s_depts = (s_depts_ & rdset)
            if len(p_depts)>0 and len(s_depts)>0:
                #print "Auto merge: %s & %s" % (str(p_depts), str(s_depts))
                choice = "y"
            if p.home_department.abbr == s.home_department.abbr and choice != "y":
                import pdb; pdb.set_trace()            
        for rdset in nrdsets:
            p_depts = (p_depts_ & rdset)
            s_depts = (s_depts_ & rdset)
            if len(p_depts)>0 and len(s_depts)>0:
                #print "Auto merge: %s & %s" % (str(p_depts), str(s_depts))
                choice = "n"
    while len(choice.strip()) == 0:
        choice = raw_input("%s merge -> %s? " % (s.short_name(True, True), p.short_name(True, True)))
    choice = choice.strip().lower()
    if choice.startswith("save"):
        choice, f = choice.split(" ")
        pickle.dump(saved, file(f, "w"))            
    if choice == "y":
        return merge_two_instructors(p, s)
    elif choice == "n":
        return p
    elif choice == "pdb":
        import pdb; pdb.set_trace()
    else:
        return prompt_candidate(p, s)
    
def prompt_candidates(primary, secondaries):
    for secondary in secondaries:
        primary = prompt_candidate(primary, secondary)
    return

    if len(secondaries) == 1:
        return prompt_candidate(primary, secondaries[0])
    choice = ""
    while len(choice.strip()) == 0:
        choice = raw_input("%s merge -> %s? " % ([s.short_name(True, True) for s in secondaries], primary.short_name(True, True)))
    choice = choice.strip().lower()
    if choice.startswith("save"):
        choice, f = choice.split(" ")
        pickle.dump(saved, file(f, "w"))        
    if choice == "y":
        winner = primary
        for s in secondaries:
            winner = merge_two_instructors(winner, s)
        print "Merged all: %s; %s" % (winner.short_name(True, True), winner.departments.all())
    elif choice == "n":
        return
    elif choice == "s":
        for secondary in secondaries:
            primary = prompt_candidate(primary, secondary)
    else:
        return prompt_candidates(primary, secondaries)
    
tried = set()
def find_merge_candidates():
#    while True:
#        instr = Instructor.objects.order_by("?")[0]
    for instr in Instructor.objects.all():
        n = "%s %s" % (len(instr.first) and instr.first[0] or '-', instr.last)
        if n in tried:
            continue
        tried.add(n)
        secondaries = Instructor.objects.exclude(pk=instr.pk).filter(last__iexact = instr.last, first__istartswith = len(instr.first) and instr.first[0] or "")
        if len(secondaries) == 0:
            continue
        prompt_candidates(instr, secondaries)
       
main = find_merge_candidates 
        
if __name__ == "__main__":
    main()

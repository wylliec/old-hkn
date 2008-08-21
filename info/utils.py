import re

def base36_to_int(s):
    return int(s, 36)

def int_to_base36(i):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    factor = 0
    # Find starting factor
    while True:
        factor += 1
        if i < 36 ** factor:
            factor -= 1
            break
    base36 = []
    # Construct base36 representation
    while factor >= 0:
        j = 36 ** factor
        base36.append(digits[i / j])
        i = i % j
        factor -= 1
    return ''.join(base36)


def normalize_email(email):
    return email.strip().lower().replace("@uclink.berkeley.edu", "@berkeley.edu").replace("@calmail.berkeley.edu", "@berkeley.edu")

def normalize_phone(phone):
    return re.sub("[^\d]", "", phone.strip())

def make_set(*args):
    s = set()
    for arg in args:
        s.add(arg)
    return s

committee_names =  {
"pres" : make_set("president", "p"),
"vp" : make_set("vicepresident", "vpres"),
"rsec" : make_set("recordingsecretary", "recsec"),
"csec" : make_set("correspondingsecretary", "corsec"),
"treas" : make_set("treasurer", "tres"),
"deprel" : make_set("departmentrelations", "departmentalrelations", "drel"),
"studrel" : make_set("studentrelations", "srel"),
"alumrel" : make_set("alumnirelations", "arel"),
"pub" : make_set("publicity"),
"examfiles" : make_set("examfile", "examfiles", "exam", "exams"),
"indrel" : make_set("industrialrelations", "irel"),
"bridge" : make_set("bridge"),
"act" : make_set("activities", "activity"),
"compserv" : make_set("compserve", "computingservice", "computerservices"),
"ejc" : make_set("ejcrepresentatives", "ejcrepresentative", "ejcrep", "erep"),
"tutor" : make_set("tutoring", "tutors"),
"alumadvisor" : make_set("alumniadvisor"),
"facadvisor" : make_set("facultyadvisor")}

def normalize_committee_name(com_name):
    com_name = com_name.strip().replace(" ", "").lower()
    for committee in committee_names.keys():
        if com_name == committee:
            return committee
        if com_name in committee_names[committee]:
            return committee
    return ""


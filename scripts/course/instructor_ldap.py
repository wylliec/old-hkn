#!/usr/bin/env python
import ldap

server = "ldap.berkeley.edu"
port = "389"
ssl_port = "636"
s_base = "dc=berkeley,dc=edu"

def get_ldap():
	l = ldap.open(server)
	l.simple_bind_s("18319533")
	return l

def lsearch(filter, l = None,ou="people", scope = ldap.SCOPE_SUBTREE, attr=None):
	if l == None:
		l = get_ldap()
	print "ldap: " + str(l)
	base = "ou=" + ou + "," + s_base
	print "base: " + base
	
	rid = l.search(base, scope, filter, attr)
	print "rid: " + str(rid)
	results = l.result(rid, all = True, timeout = 240)
	print "# results: " + str(len(results))
	return results

def get_faculty_for_dept(dept, title=None, neg = False):
	if title == None:
		return lsearch("(&(departmentNumber=%s)(berkeleyEduAffiliations=EMPLOYEE-TYPE-ACADEMIC))" % (dept,))
	if not neg:
		return lsearch("(&(departmentNumber=%s)(berkeleyEduAffiliations=EMPLOYEE-TYPE-ACADEMIC)(title=%s))" % (dept, title))
	#f =  "(&(departmentNumber=%s)(berkeleyEduAffiliations=EMPLOYEE-TYPE-ACADEMIC)(!(title=%s)))" % (dept, title)
	f =  "(&(departmentNumber=%s)(berkeleyEduAffiliations=EMPLOYEE-TYPE-ACADEMIC)(displayName<=B))" % (dept, )
	print f
	return lsearch(f)

def find_dept(query):
	return lsearch("description=*%s*" % (query,), ou="UCBKL,ou=org units", attr=("description", "berkeleyEduOrgUnitHierarchyString"))

def print_results(results):
	for r in results[1]:
		d = r[1]
		print r[0]
		for name, val in d.items():
			print "    " + str(name) + ": " + str(val)
pp  = print_results

def display_faculty(res):
	for f in res[1]:
		print f[1]['displayName']

#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup
from xml.dom import minidom
import editdist
import pdb

DEPARTMENTS_XML = "departments.xml"

def getDepartmentHash(departments):
    depts = {}
    for department in departments:
        depts[department["name"].lower()] = department["abbr"]

    return depts

depts = getDepartmentHash(BeautifulSoup(file(DEPARTMENTS_XML).read()).findAll("department"))

def findClosestName(depts, name):
    l = [(editdist.distance(k, name.lower()), k) for k in depts.keys()]
    return sorted(l, lambda x, y: cmp(x[0], y[0]))
        

def addToXml(filename, outfilename = None, verbose = False):
    f = file(filename, "r")
    xml = f.read()
    f.close()

    dom = minidom.parseString(xml)
    for department in dom.getElementsByTagName("department"):
        name = department.getAttribute("name")
        s  = findClosestName(depts, name)
        (dist, dname) = s[0]
        department.setAttribute("abbr", depts[dname])
        if verbose:
            print "%s -> %s (%s)" % (name, dname, depts[dname])
    f = file(filename, "w")
    f.write(dom.toxml())
    f.close()
        
	
def main():
	import sys
	infile = sys.argv[1]
	print "Adding to: " + infile
	addToXml(infile, verbose = True)
	
if __name__ == "__main__":
	main()


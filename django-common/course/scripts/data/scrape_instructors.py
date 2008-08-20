#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
import re, urllib2, urllib, pdb, sys
from xml.dom.minidom import Document

sys.path.append("..")
from constants import DEFAULT_DEPARTMENTS
sys.path.remove("..")

klass_ccn_pattern = re.compile("^\d{5}  $")

def clean_html(html):
	html = html.replace("&nbsp;", " ").replace("\n", "")
	html = html.replace("""<!  Office of Public Affairs and ><! IST/Student Information Systems >""", "", 1)
	html = html.replace("""<!-- A:link {color:"#000077";}A:visited {color:"#000044";}A:hover {color:"#0000CC";}-->""", "", 1)
	return html

def get_html(dept_abbr):
	url = "http://sis.berkeley.edu/catalog/gcc_view_faculty?v_dept_cd=" + dept_abbr.replace(" ", "+").upper()
	page = urllib2.urlopen(url)
	return clean_html(page.read())

def flattenXml(x):
	if isinstance(x, NavigableString):
		return x
	return "".join([flattenXml(e) for e in x.contents])

def get_instructor_name(p):
	if not is_p_contains_instructor(p):
		return None
	
	contents = p.contents
	assert len(contents) == 3, "incorrect contents: " + str(p)
	assert contents[1].name == "br", "unexpected format for name: " + str(p)
	return contents[0].strip()
	
def is_p_contains_instructor(p):
	if len(p.contents) == 3:
		return p.contents[1].name == "br" \
			and type(p.contents[0]) == NavigableString \
			and type(p.contents[2]) == NavigableString
	return False
	
def generateXmlForKlass(doc, klass):
	c = doc.createElement("klass")
	for name, val in klass.items():
		if name == "note":
			n = doc.createElement("note")
			n.appendChild(doc.createTextNode(val))
			c.appendChild(n)
		else:
			c.setAttribute(name, val)
	return c

def handleManyNames(names):
	first = names[0]
	names = names[1:]
	longestName = names[0]
	for name in names[1:]:
		if len(name) > len(longestName):
			longestName = name
	last = longestName
	if longestName == names[0]:
		middle = names[1]
		print "Middle after last?"
	else:
		middle = names[0]
	return (first, middle, last)
	

space_pattern = re.compile("\s+")
ignore_names = ("II", "III", "IV", "Jr.", "Sr.")
middle_abbr_pattern = re.compile("[A-Z]\.")
def generateXmlForInstructor(doc, instructor):
	distinguished = False
	if instructor.find("&#134;") != -1:
		distinguished = True
		instructor = instructor.replace("&#134;", "")

	grad_prof = False
	if instructor.find("&#42;") != -1:
		grad_prof = True
		instructor = instructor.replace("&#42;", "")

	old_names = names = space_pattern.split(instructor)
	names = filter(lambda name: name not in ignore_names, names)
	middle_abbrs = filter(lambda name: middle_abbr_pattern.match(name), names)
	names = filter(lambda name: name not in middle_abbrs, names)

	if len(names) >= 3 and len(middle_abbrs) > 0:
		first = names[0]
		middle = " ".join(middle_abbrs)
		last = " ".join(names[1:])
		print "Got middle name and middle abbreviations! " + instructor
		print "  --> %s %s %s" % (first, middle, last)
	elif len(names) == 3:
		(first, middle, last) = names
	elif len(names) == 2:
		(first, last) = names
		middle = " ".join(middle_abbrs)
	elif len(names) == 1:
		last = names[0]
		if len(middle_abbrs) > 0:
			first = middle_abbrs[0]
			middle = " ".join(middle_abbrs[1:])
	else:
		raise Exception, "unexpected number of names! " + instructor
	c = doc.createElement("instructor")
	c.setAttribute("first", first)
	c.setAttribute("middle", middle)
	c.setAttribute("last", last)
	if distinguished:
		c.setAttribute("distinguished", "true")
	if grad_prof:
		c.setAttribute("grad_prof", "true")
	return c
		
		
	
	

def generateXmlForInstructors(dept_abbr, instructors):
	doc = Document()
	department = doc.createElement("department")
	department.setAttribute("abbr", dept_abbr)

	for instructor in instructors:
		try: 
			department.appendChild(generateXmlForInstructor(doc, instructor))
		except Exception, e:
			print e
			pass
	doc.appendChild(department)
	return doc

def getXmlDocumentForDepartment(dept_abbr = "compsci", quiet = False):
	print "Beginning department: " + dept_abbr
	soup = BeautifulSoup(get_html(dept_abbr))
	rows = soup.findAll("p")
	instructors = []
	for r in rows:
		name = get_instructor_name(r)
		if name is None:
			continue
		instructors.append(name)
	if len(instructors) == 0:
		return None
	return generateXmlForInstructors(dept_abbr, instructors)

def get_departments():
	return DEFAULT_DEPARTMENTS

def main(departments = None):
	if departments == None:
		departments = get_departments()
	for department in departments:
		doc = getXmlDocumentForDepartment(department)
		if doc == None:
			print "None for department: " + department
			continue
		f = file("instructors_xml/" + department.replace(" ", "_") + ".xml", "w")
		f.write(doc.toprettyxml(indent="    "))

if __name__ == "__main__":
	main()


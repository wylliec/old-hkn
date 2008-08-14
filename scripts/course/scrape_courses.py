#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
import re, urllib2, urllib
from xml.dom.minidom import Document
from constants import DEFAULT_DEPARTMENTS

course_header_pattern = re.compile("^(?P<name>.*)--(?P<dept>.*) \((?P<dept_abbr>.*)\)\s+(?P<number>\S+)\s+\[(?P<units>.*)\s+units\]$")

def clean_courses_html(html):
	html = html.replace("&nbsp;", " ").replace("\n", "")
	html = html.replace("""<!  Office of Public Affairs and ><! IST/Student Information Systems >""", "", 1)
	html = html.replace("""<!-- A:link {color:"#000077";}A:visited {color:"#000044";}A:hover {color:"#0000CC";}-->""", "", 1)
	return html

def get_courses_html(dept_abbr):
	data = urllib.urlencode({"p_dept_cd" : dept_abbr})
	page = urllib2.urlopen("http://sis.berkeley.edu/catalog/gcc_search_sends_request", data)
	return clean_courses_html(page.read())

def flattenXml(x):
	if isinstance(x, NavigableString):
		return x
	return "".join([flattenXml(e) for e in x.contents])
		

def is_td_contains_course_title(td):
	if td.b != None:
		m = course_header_pattern.match(flattenXml(td.b))
#		if m is None:
#			print td.b.string
		return m
	return False

def is_tr_contains_course_title(tr):
	tds = tr.findAll("td")
	if tds != None and len(tds) > 2:
		td = tds[2]
		return is_td_contains_course_title(td)
	return False

def get_course_attribute(row):
	tds = row.findAll("td")
	assert tds != None, "no tds found for expected attribute row: " + str(row)
	if len(tds) == 1:
		assert tds[0].has_key("align"), "expected course separator row has unexpected format! " + str(row)
		return None
	assert len(tds) == 3, "unexpected number of tds for row: " + str(row)

	attribute_td = tds[2]
	td_font = attribute_td.find("font")
	assert td_font != None, "table row does not have font tag as expected! " + str(row)
	c = td_font.contents
	if len(c) > 1 and isinstance(c[1], Tag) and c[1].name == "br":
		return (None, c[0])
	header = c[0].string
	rem = []
	for e in c[1:]:
		if type(e) == 'NavigableString':
			rem.append(e)
		else:
			rem.append(e.string)
	remaining = "".join(rem)
	return (header, remaining)

def get_course_attributes(header_row):
	current_row = header_row
	attrs = {}
	attrs['unmatched'] = []
	while True:
		current_row = current_row.nextSibling
		a = get_course_attribute(current_row)
		if a == None:
			return attrs
		assert len(a) == 2, "unexpected attribute: " + str(a)
		name, val = a
		if name == None:
			attrs['unmatched'].append(val.strip())
		else:
			name = name.strip().replace(':', "").replace(" ", "_").lower()
			attrs[name] = val.strip()

def get_course_for_header_row(tr, m):
	attributes = m.groupdict()
	for name, val in attributes.items():
		attributes[name] = val.strip()

	for name, val in get_course_attributes(tr).items():
		if not attributes.has_key(name):
			attributes[name] = val
	return attributes
	
def generateXmlForCourse(doc, course):
	c = doc.createElement("course")
	c.setAttribute("name", course['name'])
	c.setAttribute("number", course['number'])
	c.setAttribute("units", course['units'])
	if course.has_key("description"):
		c.appendChild(doc.createTextNode(course['description'].strip()))
	return c
	

def generateXmlForCourses(dept_abbr, courses):
	doc = Document()

	departments = {}
	for course in courses:
		if course['dept_abbr'] not in departments.keys():
			department = doc.createElement("department")
			department.setAttribute("abbr", course['dept_abbr'])
			department.setAttribute("name", course['dept'])
			departments[course['dept_abbr']] = department
		else:
			department = departments[course['dept_abbr']]
		department.appendChild(generateXmlForCourse(doc, course))

	assert len(departments) >= 1, "got more than 1 department! " + " ".join(departments.keys())

	for abbr, dept in departments.items():
		doc.appendChild(dept)
	return doc

def getXmlDocumentForDepartment(dept_abbr = "compsci", quiet = False):
	print "Beginning department: " + dept_abbr
	soup = BeautifulSoup(get_courses_html(dept_abbr))
	table = soup.find("table")
	rows = table.findAll("tr", recursive=False)
	courses = []
	for r in rows:
		m = is_tr_contains_course_title(r)
		if not m:
			continue
		courses.append(get_course_for_header_row(r, m))
	if len(courses) == 0:
		return None
	return generateXmlForCourses(dept_abbr, courses)

def main(departments = None):
	if departments == None:
		departments = DEFAULT_DEPARTMENTS
	for department in departments:
		doc = getXmlDocumentForDepartment(department)
		if doc == None:
			print "No courses for department: " + department
			continue
		f = file("courses_xml/" + department.replace(" ", "_") + ".xml", "w")
		f.write(doc.toprettyxml(indent="    "))

if __name__ == "__main__":
	main()


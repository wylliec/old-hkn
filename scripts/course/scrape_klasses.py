#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
import re, urllib2, urllib
from xml.dom.minidom import Document
from constants import DEFAULT_DEPARTMENTS, YEAR, TERM

klass_ccn_pattern = re.compile("^\d{5}  $")

def clean_klasses_html(html):
	html = html.replace("&nbsp;", " ").replace("\n", "")
	return html

def get_klasses_html(dept_abbr):
	data = urllib.urlencode({"p_term" : TERM[0], "p_print_flag" : "Y"})
	url = "http://sis.berkeley.edu/OSOC/osoc?" + data + "&p_dept=" + dept_abbr.replace(" ", "+")
	page = urllib2.urlopen(url)
	return clean_klasses_html(page.read())

def flattenXml(x):
	if isinstance(x, NavigableString):
		return x
	return "".join([flattenXml(e) for e in x.contents])
		

def is_td_contains_ccn(td):
	if td.font != None:
		m = klass_ccn_pattern.match(flattenXml(td.font))
		return m
	return False

def is_tr_contains_ccn(tr):
	tds = tr.findAll("td")
	if tds != None and len(tds) == 11:
		td = tds[1]
		return is_td_contains_ccn(td)
	return False

def get_klass_for_main_row(tr):
	tds = tr.findAll("td")
	get_text_for_cell = lambda x: flattenXml(tds[x].font).strip()
	klass = {}
	klass['ccn'] = get_text_for_cell(1)
	klass['number_type'], klass['number'] = get_text_for_cell(2).split("  ")
	klass['section'] = get_text_for_cell(3)
	klass['time'] = get_text_for_cell(4)
	klass['room'] = get_text_for_cell(5)
	klass['name'] = get_text_for_cell(6)
	klass['units'] = get_text_for_cell(7)
	klass['instructor'] = get_text_for_cell(8)
	klass['exam_group'] = get_text_for_cell(9)
	klass['restrictions'] = get_text_for_cell(10)
	return klass

def get_note_from_row(tr):
	note_td = tr.find("td", colspan="9")
	if note_td is None:
		return None
	assert note_td.font != None or len(note_td.font.contents) == 1, "note td font was none or len 1 " + str(tr)
	contents = note_td.font.contents
	assert contents[0].string == "Note: ", "unexpected note header, wanted \"Note: \" but got: \"" + contents[0].string + "\""
	return "".join([flattenXml(e) for e in contents[1:]])
	

def get_klass_for_header_row(tr):
	klass = get_klass_for_main_row(tr)
	next_tr = tr.findNextSibling("tr")
	if next_tr != None:
		note = get_note_from_row(next_tr)
		if note != None:
			klass["note"] = note.strip()
	return klass
	
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
	

def generateXmlForKlasses(dept_abbr, klasses):
	doc = Document()
	semester = doc.createElement("semester")
	semester.setAttribute("year", str(YEAR))
	semester.setAttribute("season", TERM[1])
	department = doc.createElement("department")
	department.setAttribute("abbr", dept_abbr)

	for klass in klasses:
		department.appendChild(generateXmlForKlass(doc, klass))

	semester.appendChild(department)
	doc.appendChild(semester)
	return doc

def getXmlDocumentForDepartment(dept_abbr = "compsci", quiet = False):
	print "Beginning department: " + dept_abbr
	soup = BeautifulSoup(get_klasses_html(dept_abbr))
	table = soup.find("table")
	if table == None:
		return None
	rows = table.findAll("tr", recursive=False)
	klasses = []
	for r in rows:
		m = is_tr_contains_ccn(r)
		if not m:
			continue
		klasses.append(get_klass_for_header_row(r))
	if len(klasses) == 0:
		return None
	return generateXmlForKlasses(dept_abbr, klasses)

def get_departments():
	return DEFAULT_DEPARTMENTS
#	import glob
#	fs = glob.glob("courses_xml/*xml")
#	dpts = []
#	for f in fs:
#		f = f.replace("courses_xml/", "").replace(".xml", "").replace("_", " ")
#		dpts.append(f)
#	return dpts
	

def main(departments = None):
	if departments == None:
		departments = get_departments()
	for department in departments:
		doc = getXmlDocumentForDepartment(department)
		if doc == None:
			print "No klasses for department: " + department
			continue
		f = file("klasses_xml/" + department.replace(" ", "_") + ".xml", "w")
		f.write(doc.toprettyxml(indent="    "))

if __name__ == "__main__":
	main()


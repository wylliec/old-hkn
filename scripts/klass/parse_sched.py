import re
import pdb
from xml.dom.minidom import Document

match_float = r'-?\d+(\.\d+)?'
match_tf = "/(?P<font>.*) " + match_float + " Tf"
match_tj = "\((?P<value>.*)\) " + match_float + " Tj"
match_td = "(?P<x>" + match_float + ") (?P<y>" + match_float + ") Td"
match_semester = "\([^,]*, (?P<season>.*) (?P<year>.*)\) " + match_float + " Tj"

match_page_start = "\n\[1 0 0 1 0 0\] Tm\n0 0 Td\n"
match_page_end = ".*Tf\n.*Tj\nQ\nQ\nshowpage"
match_doc_start = "\n%%EndSetup\n"
match_doc_end = ".*Tf\n\(Total: \d+\) " + match_float + " Tj\n"
match_doc_end_alt = ".*Tf\n\(.*The Regents of the University of California.*\\\n.*\) " + match_float + " Tj\n"


pattern_float = re.compile(match_float)
pattern_td = re.compile(match_td)
pattern_tf = re.compile(match_tf)
pattern_tj = re.compile(match_tj)
pattern_semester = re.compile(match_semester)

pattern_page_start = re.compile(match_page_start)
pattern_page_end = re.compile(match_page_end)
pattern_doc_start = re.compile(match_doc_start)
pattern_doc_end = re.compile(match_doc_end)
pattern_doc_end_alt = re.compile(match_doc_end_alt)


def get_main_text(fname):
	u = file(fname, "r").read()
	doc_start = pattern_doc_start.search(u).end()
	try:
		doc_end = pattern_doc_end.search(u).start()
	except:
		doc_end = pattern_doc_end_alt.search(u).start()
	return u[doc_start:doc_end]

def get_pages(u):
	def cutPage(i, pg, last_page):
		if i == last_page:
			return pg
		mtch = pattern_page_end.search(pg)
		if mtch == None:
			return ""
		page_end = pattern_page_end.search(pg).start()
		return pg[:page_end]
	pgs = pattern_page_start.split(u)
	last_page = len(pgs) - 1
	pgs2 = [cutPage(i, pg, last_page) for i, pg in enumerate(pgs)]
	pgs3 = [pg for pg in pgs2 if len(pg) > 0]
	return pgs3

def get_rows_for_page(page):
	page = page.replace("\\\n", "")
	rows = page.split("\n")
	return rows
	
def get_rows(pages):
	rows = [get_rows_for_page(page) for page in pages]
	semester_row = None
	for row in rows[0]:
		if not row.endswith("Tj"):
			continue
		semester_row = row
		rows[0].remove(row)
		break
	return (rows, semester_row)
	
def get_semester(semester_row):
	mtch = pattern_semester.match(semester_row)
	return (mtch.group("season"), mtch.group("year"))
	
	
from string import atof
def are_close(x1, x2, precision=.001):
	diff = abs(atof(x1) - atof(x2))
	return diff < precision
	
def rowsToXmlPage(doc, rows):
#	page = doc.createElement("page")
	fonts = []
	lastX = "-99999999"
	lastY = "-99999999"
	lastCell = None
	lastFont = None
	currentX = "-1234567"
	currentY = "-1234567"
	currentFont = None
	for row in rows:
		if row.endswith("Tf"):
			if currentFont is not None:
#				page.appendChild(currentFont)
				fonts.append(currentFont)
			currentFont = doc.createElement("font")
			mtch = pattern_tf.match(row)
			currentFont.setAttribute("id", mtch.group("font"))			
		elif row.endswith("Td"):
			mtch = pattern_td.match(row)
			currentX = mtch.group("x")
			currentY = mtch.group("y")			
		elif row.endswith("Tj"):
			mtch = pattern_tj.match(row)
			value = mtch.group("value")
			
			if are_close(lastX, currentX) and \
				(are_close(lastY, currentY) or currentFont == lastFont):
				# we only add the current value to the last cell's value in one of two cases:
				# 1. Both the X and Y coordinates are the same (this happens with notes
				#    the x, y are the same but the font is different
				# 2. The X coordinate is the same and the fonts are the same (this happens
				#    with table headers, the x and font are the same but the y is different
				lastCell.setAttribute("value", lastCell.getAttribute("value") + " " + value)
			else:
				cell = doc.createElement("cell")
				cell.setAttribute("value", value)
				cell.setAttribute("x", currentX)
				cell.setAttribute("y", currentY)
				currentFont.appendChild(cell)
				lastCell = cell
				
			lastX = currentX
			lastY = currentY
			lastFont = currentFont
			
		elif row.endswith("Tc"):
			pass
	if currentFont != None:
#		page.appendChild(currentFont)
		fonts.append(currentFont)
#	return page
	return fonts
	
def rowsToXmlDocument(rowsArray, season, year):
	doc = Document()
	schedule = doc.createElement("schedule")
	schedule.setAttribute("season", season)
	schedule.setAttribute("year", year)	
	
	doc.appendChild(schedule)
	
	for rows in rowsArray:
#		page = rowsToXmlPage(doc, rows)
#		schedule.appendChild(page)		
		fonts = rowsToXmlPage(doc, rows)
		for font in fonts:
			schedule.appendChild(font)
	
	return doc

def writeToXmlFile(doc, filename):
	f = file(filename, "w")
	f.write(doc.toprettyxml(indent="    "))
	
	
def parseSchedule(filename, outfilename = None):
	u = get_main_text(filename)
	pages = get_pages(u)
	(rows, semester_row) = get_rows(pages)
	(season, year) = get_semester(semester_row)
	doc = rowsToXmlDocument(rows, season, year)
	if outfilename == None:
		outfilename = season + "-" + year + "-intermediate.xml"
	writeToXmlFile(doc, outfilename)
	


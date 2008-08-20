#!/usr/bin/python
import re
import pdb
from xml.dom import minidom
from string import atof, atoi

NOTE_FONT_ID = "F8_0"
TABLE_HEADER_FONT_ID = "F5_0"
DEPARTMENT_HEADER_FONT_ID = "F6_0"

def is_department_header_cell(cell):
	return cell.parentNode.getAttribute("id") == DEPARTMENT_HEADER_FONT_ID
	
def is_table_header_cell(cell):
	return cell.parentNode.getAttribute("id") == TABLE_HEADER_FONT_ID
	
def is_note_cell(cell):
	return cell.parentNode.getAttribute("id") == NOTE_FONT_ID

class Headers(object):
	def __init__(self, headers):
		self.headers = {}
		for header in headers:
			header_name = header.getAttribute("value").strip().lower().replace(" ", "_")
			header_x = atof(header.getAttribute("x"))
			self.headers[header_x] = header_name
			
	def get_nearest_header(self, x):
		closest_header_x = -99999999
		for header_x in self.headers.keys():
			if abs(header_x - x) < abs(closest_header_x - x):
				closest_header_x = header_x				
		return self.headers[closest_header_x]

def are_close(x1, x2, precision=.001):
	diff = abs(atof(x1) - atof(x2))
	return diff < precision		

def getDepartmentXml(department_name, cells, doc):
	assert cells[0].parentNode.getAttribute("id") == TABLE_HEADER_FONT_ID, "First cell should be a table header with expected font id %s, but got %s!" % (TABLE_HEADER_FONT_ID, cells[0].parentNode.getAttribute("id"))
	header_cells = []
	for i, cell in enumerate(cells):
		if is_table_header_cell(cell):
			header_cells.append(cell)
		else:
			cells = cells[i+1:]
			break
			
	headers = Headers(header_cells)

	dpt = doc.createElement("department")	
	dpt.setAttribute("name", department_name)
	
	currentKlass = doc.createElement("klass")
	lastY = -99999	
	for cell in cells:
		value = cell.getAttribute("value").strip()		
	
		if is_note_cell(cell):
			currentKlass.setAttribute("note", value)
			continue			
			
		currentX = atof(cell.getAttribute("x"))	
		currentY = atof(cell.getAttribute("y"))
		if not are_close(lastY, currentY):
			# new row
			currentKlass = doc.createElement("klass")			
			dpt.appendChild(currentKlass)
		name = headers.get_nearest_header(currentX)
		currentKlass.setAttribute(name, value)
		lastY = currentY
	dpt.appendChild(currentKlass)		
	return dpt
	
def is_v3(dom):
	schedule = dom.getElementsByTagName("schedule")[0]
	season = schedule.getAttribute("season")
	year = schedule.getAttribute("year")
	yr = atoi(year)
	
	# version 3 for fall2005 and beyond
	if yr > 2005:
		return True
	if yr == 2005 and season.lower() == "fall":
		return True
	return False 	

def get_transformed_xml_document(dom):	
	schedule = dom.getElementsByTagName("schedule")[0]
	season = schedule.getAttribute("season")
	year = schedule.getAttribute("year")	
	
	cells = schedule.getElementsByTagName("cell")
	assert cells[0].parentNode.getAttribute("id") == DEPARTMENT_HEADER_FONT_ID, "First cell should be a department header with expected font id %s, but got %s!" % (DEPARTMENT_HEADER_FONT_ID, cells[0].parentNode.getAttribute("id"))
	
	department_indicies = [cell_index for cell_index, cell in enumerate(cells) if is_department_header_cell(cell)]		
	
	departments = []
	doc = minidom.Document()	
	for i, department_index in enumerate(department_indicies):
		try:
			next_department_index = department_indicies[i+1]
		except:
			next_department_index = len(cells)
			
		cell = cells[department_index]
		department_name = cell.getAttribute("value")
		dept = getDepartmentXml(department_name, cells[department_index+1:next_department_index], doc)
		departments.append(dept)
		
	semester = doc.createElement("semester")
	semester.setAttribute("season", season)
	semester.setAttribute("year", year)
	doc.appendChild(semester)
	for dpt in departments:
		semester.appendChild(dpt)
	return (doc, season, year)
	
def writeToXmlFile(doc, filename):
	f = file(filename, "w")
	f.write(doc.toprettyxml(indent="    "))
	
def transformXml(dom, filename = None, outfilename = None):
	if dom == None:
		dom = minidom.parse(file(filename, "r"))
	(doc, season, year) = get_transformed_xml_document(dom)
	if outfilename == None:
		outfilename = season + "-" + year + ".xml"
	writeToXmlFile(doc, outfilename)

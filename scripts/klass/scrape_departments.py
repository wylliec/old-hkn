#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup
from xml.dom.minidom import Document
import pdb

def parseDepartmentAbbrs(soup):
    def hasChild(element, child_tag):
        for c in element.findChildren():
            if c.name == child_tag:
                return True
        return False

    def font_filter(font):
        if not font.name == "font":
            return False
        if not (font.has_key("size") and font["size"] == "1"):
            return False
        if font.parent.name == "td":
            td = font.parent
            if td.has_key("valign") and td["valign"] == "TOP":
                return True
        return False
        
    departments = []
    abbrs = []
    abbrTable = soup.find("table", width="370")
    fonts = abbrTable.findAll(font_filter)
    for font in fonts:
        if hasChild(font, "a"):
            departments.append(font.a.contents[0])
            for sibling in font.findNextSiblings():
                departments.append(sibling.contents[0])
        else:
            abbrs.append(font.contents[0])
            for sibling in font.findNextSiblings():
                abbrs.append(sibling.contents[0])

    abbrs = [abbr.replace(" ", "").replace("&nbsp;", " ") for abbr in abbrs]
    depts = zip(departments, abbrs)
    return depts

def generateXmlForDepartment(doc, dept):
    d = doc.createElement("department")
    d.setAttribute("name", dept[0])
    d.setAttribute("abbr", dept[1])
    return d 
    

def generateXmlForDepartments(depts):
    doc = Document()
    university = doc.createElement("university")
    university.setAttribute("name", "UC Berkeley")
    for dept in depts:
        try:
            university.appendChild(generateXmlForDepartment(doc, dept))
        except Exception, e:
            print e
            pass
    doc.appendChild(university)
    return doc
        
        

def main(filename):
    html = open(filename)
    soup = BeautifulSoup(html)
    depts = parseDepartmentAbbrs(soup)
    doc = generateXmlForDepartments(depts)
    f = file("departments.xml", "w")
    f.write(doc.toprettyxml(indent="    "))
    
if __name__ == "__main__":
    main("cached_pages/deptabb.html")   

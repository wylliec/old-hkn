#!/usr/bin/env python
import pdb
import glob, os
import parse_sched as ps
import transform_xml as tx
import add_department_abbr_to_xml as add_department_abbrs

def convert(psFile, intermediateFile = None, finalFile = None):
    try:
        convert_to_intermediate(psFile, intermediateFile)
        convert_to_final(intermediateFile, finalFile)
    except Exception, e:
        pdb.set_trace()
    
def convert_to_intermediate(psFile, intermediateFile = None):
    if intermediateFile == None:
        intermediateFile = psFile.replace("ps/", "intermediate_xml/").replace(".ps", "-intermediate.xml")
    if os.path.exists(intermediateFile):
        print "Intermediate file already exists: " + intermediateFile
        return
        
    print "Working on: " + psFile
    ps.parseSchedule(psFile, intermediateFile)                
        
        
def convert_to_final(intermediateFile, finalFile = None):
    if finalFile == None:
        finalFile = intermediateFile.replace("intermediate_xml/", "xml/").replace("-intermediate.xml", ".xml")
    if os.path.exists(finalFile):
        print "Final file already exists: " + finalFile
        return
        
    print "Working on: " + intermediateFile
    tx.transformXml(intermediateFile, finalFile)
    
def convert_all_to_final():
    psFiles = glob.glob("intermediate_xml/*.xml")
    for psFile in psFiles:
        convert_to_final(psFile)    

def convert_all_to_intermediate():
    psFiles = glob.glob("ps/*ps")
    for psFile in psFiles:
        convert_to_intermediate(psFile)

def add_dept_abbr_to_all():
    xmlFiles = glob.glob("xml/*.xml")
    for xmlFile in xmlFiles:
        add_department_abbrs.addToXml(xmlFile)

def convert_all():
    convert_all_to_intermediate()
    convert_all_to_final()    
    add_dept_abbr_to_all()
        
if __name__ == "__main__":
    convert_all()

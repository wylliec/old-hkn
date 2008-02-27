#!/usr/bin/env python
import transform_xml_v1 as tx1
import transform_xml_v2 as tx2
import transform_xml_v3 as tx3
from xml.dom import minidom
import pdb


def get_transform_module(dom):
	if tx3.is_v3(dom):
		return tx3
	elif tx2.is_v2(dom):
		return tx2
	else:
		return tx1
		
def transformXml(filename, outfilename = None):
	dom = minidom.parse(file(filename, "r"))
	tx = get_transform_module(dom)
	print "Using: " + tx.__name__
	tx.transformXml(dom, outfilename=outfilename)
	
def main():
	import sys
	infile = sys.argv[1]
	print "Transforming: " + infile
	transformXml(infile)
	
if __name__ == "__main__":
	main()

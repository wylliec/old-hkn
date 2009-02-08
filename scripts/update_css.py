#!/usr/bin/env python
import os, glob, shutil

os.chdir("..")
os.system("compass -u sass")

files = glob.glob("sass/stylesheets/*css")
for file in files:
    print "Copying %s" % file
    shutil.copy(file, "static/css")

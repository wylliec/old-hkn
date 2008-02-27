#!/usr//bin/env python

f = file("initiates.txt")

currentOutFile = None

for l in f:
    l = l.strip()
    if l.endswith(":"):
        if currentOutFile:
            currentOutFile.close()
        currentOutFile = file("initiates_" + l[:-1].lower().replace(" ", "") + ".txt", "w")
        continue
    if len(l.strip()) > 0 and currentOutFile is not None:
        currentOutFile.write(l.strip() + "\n")

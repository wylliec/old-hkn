#!/usr/bin/env python
import setup_settings
from django.template import Template, Context
import os, glob

def main():
    f = open("../title_xxxx.tex")
    t = Template(f.read())
    f.close()

    years = list(xrange(1990, 2050))
    years.append("grads")
    for year in years:
        c = Context({"year":year})
        tt = t.render(c)
        f = open("title_%s.tex" % year, "w")
        f.write(tt)
        f.close()
    for tex in glob.glob("*.tex"):
        os.system("pdflatex %s" % tex)

if __name__ == "__main__":
    main()


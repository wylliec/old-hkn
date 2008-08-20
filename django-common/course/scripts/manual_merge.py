#!/usr/bin/env python
import os
import setup_settings; setup_settings.setup(); os.chdir(setup_settings.get_cd())

from course.models import *
import merge_instructors

to_merge = (
("Kiureghian, A", "Derkiureghian, A [CIVE]"),
("Tilley, Don", "Tilley, T"),
("Bishop, J [EPS]", "Bishop, J [IB]"),
("Ibbs, W", "Ibbs, C"),
("Whaley, Birgitta [CHEM]", "Whaley, K [CHEM]"),
("Vollhardt, K [CHEM]", "Vollhardt, Peter [CHEM]"),
)

def merge_cached():
    for p_q, s_q in to_merge:
        p = Instructor.objects.ft_query(p_q, exact=True)
        s = Instructor.objects.ft_query(s_q, exact=True)
        if len(p) != 1:
            print "Query for %s yielded %d: %s" % (p_q, len(p), [i.short_name(True, True) for i in p])
            continue
        if len(s) != 1:
            print "Query for %s yielded %d: %s" % (s_q, len(s), [i.short_name(True, True) for i in s])
            continue
        if p[0] == s[0]:
            print "Query for %s and %s yielded the same object!" % (p_q, s_q)
            continue
        else:
            merge_instructors.merge_two_instructors(p[0], s[0])
main = merge_cached

if __name__ == "__main__":
    main()

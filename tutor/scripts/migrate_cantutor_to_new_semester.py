#!/usr/bin/env python
import setup_settings
from nice_types import semester

from hkn.info.models import *
from hkn.tutor.models import CanTutor


current_semester = semester.current_semester()
previous_semester = current_semester.previous_semester
def main():
    for officer in Person.officers.all():
        for ct in CanTutor.objects.filter(person=officer, semester=previous_semester):
            CanTutor.objects.create(person=officer, semester=current_semester, course=ct.course, current=False)


if __name__ == "__main__":
    main()
     

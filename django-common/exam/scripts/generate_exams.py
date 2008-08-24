#!/usr/bin/env python

import setup_settings

from course.models import *
from exam.models import *
from exam.constants import EXAM_TYPE
import random, datetime

def createExamForKlass(k, tp, num):
    e = Exam()
    e.klass = k
    e.file = None
    e.exam_type = tp
    e.number = num
    e.version = 0
    e.is_solution = random.random() < 0.5
    e.paper_only = random.random() < 0.05
    e.publishable = random.random() < 0.90
    e.topics = ""
    e.submitter = None
    e.save()
    

def createExamsForKlass(k):
    pop = ((EXAM_TYPE.MIDTERM, 1), (EXAM_TYPE.MIDTERM, 2), (EXAM_TYPE.MIDTERM, 3), (EXAM_TYPE.FINAL, 1), (EXAM_TYPE.QUIZ, 2), (EXAM_TYPE.REVIEW, 1))
    for p in random.sample(pop, 3):
        createExamForKlass(k, p[0], p[1])

def main():
    depts = ["COMPSCI", "EL ENG"]
    klasses = list(Klass.objects.filter(course__department_abbr__in = depts))
    for k in klasses:
        createExamsForKlass(k)

if __name__ == "__main__":
    main()

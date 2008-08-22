#!/usr/bin/env python

import hkn_settings

from review.models import *
from django.core.files.base import ContentFile

import random, datetime

tags = ['ee20', 'ee40', 'cs61a', 'cs61b', 'cs61c', 'fourier series', 'circuits', 'django', 'ruby on rails', 'eecs', 'blackberry', 'babak', 'exam problem', 'state machines', 'probability', 'combinatorics', 'berkeley', 'your face', 'nir ackner', 'aiMEE', 'help me im trapped in a tag factory']

question_file = ContentFile('a question')
answer_file = ContentFile('an answer')

def generate_review():
    tagz = random.sample(tags, random.randint(3, 6))
    p = Problem()
    p.name = "a problem incorporating %s" % (', '.join(tagz),)
    p.tags = ', '.join(tagz)
    p.difficulty = random.randint(1,5)
    rn = random.randint(1, 10000)
    p.question.save('q%d.pdf' % rn, question_file)
    p.answer.save('a%d.pdf' % rn,answer_file)
    p.save()



def main():
    num_problems = random.randint(40, 50)
    for i in range(num_problems):
        generate_review()
    

if __name__ == "__main__":
    main()

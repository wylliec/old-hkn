#!/usr/bin/env python

import hkn_settings

from review.models import *
from django.core.files.uploadedfile import SimpleUploadedFile

import random, datetime

tags = ['ee20', 'ee40', 'cs61a', 'cs61b', 'cs61c', 'fourier series', 'circuits', 'django', 'ruby on rails', 'eecs', 'blackberry', 'babak', 'exam problem', 'state machines', 'probability', 'combinatorics', 'berkeley', 'your face', 'nir ackner', 'aiMEE', 'help me im trapped in a tag factory']

def generate_review():
    tagz = random.sample(tags, random.randint(3, 6))
    p = Problem()
    p.name = "a problem incorporating %s" % (', '.join(tagz),)
    p.tags = ', '.join(tagz)
    p.difficulty = random.randint(1,5)
    rn = random.randint(1, 10000)
    question_file = SimpleUploadedFile('q%d.pdf' % rn, 'a question')
    p.question.save('q%d.pdf' % rn, question_file)
    answer_file = SimpleUploadedFile('a%d.pdf' % rn, 'an answer')
    p.answer.save('a%d.pdf' % rn,answer_file)
    p.save()



def main():
    num_problems = random.randint(40, 50)
    for i in range(num_problems):
        generate_review()
    

if __name__ == "__main__":
    main()

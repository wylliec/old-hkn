from hkn.cand.models import CandidateQuiz
import re

def c(str):
    return re.compile(str, re.IGNORECASE)

q1_ans = c('(Illinois|UIUC|Urbana)')
q2_ans = c('1904')
q3_ans = c('mu')
q4_ans = c('1915')
q5_ans = [c('(scarlet)'),
          c('(navy blue|navy-blue)')]
q6_ans = c('wheatstone bridge')
q7_ans = [c('vice president'),
          c('president'),
          c('recording secretary'),
          c('faculty advisor'),
          c('corresponding secretary'),
          c('advisor')]
q8_ans = [c('exams'),
          c('tutor'),
          c('course survey'),
          c('advising')]
q9_ans = [(c('sahai'), ,c('')),
          (c('garcia'), c('beta theta')),]
q10_ans = [c('345 soda'),
           c('290 cory')]
q11_ans = c('(470/27|17.4)')

def check_q1(answers, cquiz):
    if q1_ans.search(sanitize(answers[0])):
        cquiz.q1b = True

def check_q2(answers, cquiz):
    if q2_ans.search(sanitize(answers[0])):
        cquiz.q2b = True

def check_q3(answers, cquiz):
    if q3_ans.search(sanitize(answers[0])):
        cquiz.q3b = True

def check_q4(answers, cquiz):
    if q4_ans.search(sanitize(answers[0])):
        cquiz.q4b = True

def check_q5(answers, cquiz):
    for j in q5_ans:
        for i in answers:
            if j.search(sanitize(answers)):
                answers.remove(i)
                break
            
    if len(answers) == 0:
        cquiz.q5b = True

def check_q6(answers, cquiz):
    if q6_ans.search(sanitize(answers[0])):
        cquiz.q6b = True

def check_q7(answers, cquiz):
    for j in q7_ans:
        for i in answers:
            if j.search(sanitize(answers)):
                answers.remove(i)
                break
            
    if len(answers) == 0:
        cquiz.q7b = True

def check_q8(answers, cquiz):
    for j in q8_ans:
        for i in answers:
            if j.search(sanitize(answers)):
                answers.remove(i)
                break
            
    if len(answers) == 0:
        cquiz.q8b = True

def check_q9(answers, cquiz):
    for i in q9_ans:
            if i[0].search(sanitize(answers[0])) and i[1].search(sanitize(answers[1])):
                answers.remove(i)
                break
            
    if len(answers) == 0:
        cquiz.q9b = True

def check_q10(answers, cquiz):
    for j in q10_ans:
        for i in answers:
            if j.search(sanitize(answers)):
                answers.remove(i)
                break
            
    if len(answers) == 0:
        cquiz.q10b = True

def check_q11(answers, cquiz):
    if q11_ans.search(sanitize(answers[0])):
        cquiz.q11b = True

def sanitize(str):
    return str.trim()
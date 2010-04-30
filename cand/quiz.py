from hkn.cand.models import CandidateQuiz
import re

def c(str):
  return re.compile(str, re.IGNORECASE)

q1_ans = c('(UIUC|Urbana Champaign|Urbana-Champaign)')
#q1_partial_ans = c('(University of Illinois)')
q2_ans = c('1904')
q3_ans = c('mu')
q4_ans = c('1915')
q5_ans = [c('(scarlet)'),
    c('(navy blue|navy-blue)')]
q6_ans = c('wheatstone bridge')
q7_ans = [c('vice president|vice-president'),
    c('president'),
    c('recording secretary'),
    c('bridge correspondent'),
    c('corresponding secretary'),
    c('treasurer')]
q8_ans = [c('exam'),
    c('tutor'),
    c('course survey'),
    c('advising'),
    c('food run'),
    c('review session'),
    c('faculty retreat presentation'),
    c('department bake(.*)off')]
q9_ans = [(c('sahai'), c('mu|berkeley')),
    (c('garcia'), c('beta theta|mit')),
    (c('birdsall'), c('beta epsilon|michigan')),
    (c('babak|ayazifar'), c('iota pi|caltech')),]
q10_ans = [c('345 soda|soda 345'),
    c('290 cory|cory 290')]
q11_ans = c('(470/27|17.4|17)')

def check_q1(answers, cquiz):
  cquiz.q1 = sanitize(answers[0])
  if q1_ans.search(sanitize(answers[0])):
    cquiz.q1b = True
    cquiz.score += 1
#  else:
#    cquiz.q1b = False
#    if q1_partial_ans.search(sanitize(answers[0])):
#      cquiz.score += 0.5

def check_q2(answers, cquiz):
  cquiz.q2 = sanitize(answers[0])
  if q2_ans.search(sanitize(answers[0])):
    cquiz.q2b = True
    cquiz.score += 1
  else:
    cquiz.q2b = False

def check_q3(answers, cquiz):
  cquiz.q3 = sanitize(answers[0])
  if q3_ans.search(sanitize(answers[0])):
    cquiz.q3b = True
    cquiz.score += 1
  else:
    cquiz.q3b = False

def check_q4(answers, cquiz):
  cquiz.q4 = sanitize(answers[0])
  if q4_ans.search(sanitize(answers[0])):
    cquiz.q4b = True
    cquiz.score += 1
  else:
    cquiz.q4b = False

def check_q5(answers, cquiz):
  cquiz.q51 = sanitize(answers[0])
  cquiz.q52 = sanitize(answers[1])
  for j in q5_ans:
    for i in answers:
      if j.search(sanitize(i)):
        answers.remove(i)
        break

  if len(answers) == 0:
    cquiz.q5b = True
    cquiz.score += 1
  else:
    cquiz.q5b = False
    if len(answers) == 1:
      cquiz.score += 0.5

def check_q6(answers, cquiz):
  cquiz.q6 = sanitize(answers[0])
  if q6_ans.search(sanitize(answers[0])):
    cquiz.q6b = True
    cquiz.score += 1
  else:
    cquiz.q6b = False

def check_q7(answers, cquiz):
  cquiz.q71 = sanitize(answers[0])
  cquiz.q72 = sanitize(answers[1])
  cquiz.q73 = sanitize(answers[2])
  cquiz.q74 = sanitize(answers[3])
  cquiz.q75 = sanitize(answers[4])
  cquiz.q76 = sanitize(answers[5])
  for j in q7_ans:
    for i in answers:
      if j.search(sanitize(i)):
        answers.remove(i)
        break

  if len(answers) == 0:
    cquiz.q7b = True
    cquiz.score += 1
#  else:
#    cquiz.q7b = False
#    if len(answers) == 1:
#      cquiz.score += 0.5

def check_q8(answers, cquiz):
  cquiz.q81 = sanitize(answers[0])
  cquiz.q82 = sanitize(answers[1])
  cquiz.q83 = sanitize(answers[2])
  cquiz.q84 = sanitize(answers[3])
  for j in q8_ans:
    for i in answers:
      if j.search(sanitize(i)):
        answers.remove(i)
        break

  if len(answers) == 0:
    cquiz.q8b = True
    cquiz.score += 1
  # Removed partial credit
  #else:
  #  cquiz.q8b = False
  #  if len(answers) == 1:
  #    cquiz.score += 0.5

def check_q9(answers, cquiz):
  cquiz.q91 = sanitize(answers[0])
  cquiz.q92 = sanitize(answers[1])
  match = False
  for i in q9_ans:
    if i[0].search(sanitize(answers[0])) and i[1].search(sanitize(answers[1])):
      match = True
      cquiz.score += 1
      break

  if match:
    cquiz.q9b = True
  else:
    cquiz.q9b = False

def check_q10(answers, cquiz):
  cquiz.q101 = sanitize(answers[0])
  cquiz.q102 = sanitize(answers[1])
  for j in q10_ans:
    for i in answers:
      if j.search(sanitize(i)):
        answers.remove(i)
        break

  if len(answers) == 0:
    cquiz.q10b = True
    cquiz.score += 1
  else:
    cquiz.q10b = False

def check_q11(answers, cquiz):
  cquiz.q11 = sanitize(answers[0])
  if q11_ans.search(sanitize(answers[0])):
    cquiz.q11b = True
    cquiz.score += 1
  else:
    cquiz.q11b = False

def sanitize(str):
  return str.strip()

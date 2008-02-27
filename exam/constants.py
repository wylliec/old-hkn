from hkn.enum import EnumType

FILE_UPLOAD_DIR = 'exam'

VALID_EXTENSIONS = ["doc", ".pdf", ".html", ".htm", ".txt"]

EXAM_TYPE_MIDTERM = "mt"
EXAM_TYPE_FINAL = "f"
EXAM_TYPE_QUIZ = "q"
EXAM_TYPE_REVIEW = "r"

EXAM_TYPE = EnumType(MIDTERM = EXAM_TYPE_MIDTERM, FINAL = EXAM_TYPE_FINAL, QUIZ = EXAM_TYPE_QUIZ, REVIEW = EXAM_TYPE_REVIEW)
EXAM_TYPE.add_descriptions(((EXAM_TYPE.MIDTERM, "Midterm"), (EXAM_TYPE.FINAL, "Final"), (EXAM_TYPE.QUIZ, "Quiz"), (EXAM_TYPE.REVIEW, "Review")))

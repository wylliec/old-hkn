from django.core import urlresolvers
from models import Exam
import request

def get_exam_metainfo(exam, request):
    metainfo = {}

    metainfo['title'] = "Confirm Exam"
    metainfo['links'] = [("file", exam.file.url),
                     ("info", urlresolvers.reverse("exam-view", kwargs = {"exam_id" : exam.id})),]
    metainfo['confirmed'] = exam.publishable                     
    if exam.submitter:
        metainfo['description'] = "Confirm Exam from %s: %s" % (exam.submitter.name, exam.get_exam_description(course=True, semester=True, instructor=True))
        metainfo['links'].append(("submitter", urlresolvers.reverse("person-view", kwargs = {"person_id" : exam.submitter.id})))
    else:
        metainfo['description'] = "Confirm Exam from Anonymous: %s" % exam.get_exam_description(course=True, semester=True, instructors=True)
    return metainfo

request.register(Exam, get_exam_metainfo, confirmation_attr='publishable')

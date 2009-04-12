from hkn.cand.models import CourseSurvey
import request

def get_survey_metainfo(survey, request):
    metainfo = {}

    metainfo['title'] = "Approve Course Survey"
    metainfo['links'] = [("", "")]
    metainfo['confirmed'] = survey.status
    metainfo['description'] = "Confirm %s %s's course survey: %s" % (survey.surveyor.first_name, survey.surveyor.last_name, survey.klass)

    return metainfo

request.register(CourseSurvey, get_survey_metainfo, confirmation_attr='status')

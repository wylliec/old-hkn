from hkn.cand.models import Challenge
import request

def get_challenge_metainfo(challenge, request):
    metainfo = {}

    metainfo['title'] = "Approve Challenge"
    metainfo['links'] = [("", "")]
    metainfo['confirmed'] = challenge.status
    metainfo['description'] = "Confirm %s %s's challenge" % (challenge.candidate.first_name, challenge.candidate.last_name)

    return metainfo

request.register(Challenge, get_challenge_metainfo, confirmation_attr='status')

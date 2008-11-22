from hkn.sms.module_interface import sms_handler

@sms_handler(r'who am i')
def who_am_i(user, message, match):
    return "You are %s" % user.username

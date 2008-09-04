#!/usr/bin/env python
import PAM

__all__ = ["authenticate"]

def authenticate(username, password, service="login"):
    def pam_conv(auth, query_list, userData):
        resp = []
        for i in range(len(query_list)):
            query, type = query_list[i]
            if type == PAM.PAM_PROMPT_ECHO_OFF and query.lower().find("pass") != -1:
                resp.append((password, 0))
                print "setting password"
            elif type == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                print query
                resp.append(('', 0))
            else:
                print "PAM UNKNOWN QUERY"
                return None
        return resp

    auth = PAM.pam()
    auth.start(service)
    auth.set_item(PAM.PAM_USER, username)
    #auth.set_item(6, password)
    auth.set_item(PAM.PAM_CONV, pam_conv)
    try:
        auth.authenticate()
        print "Success"
    except PAM.error, resp:
        print "Error: %s" % resp


if __name__ == "__main__":
        import sys
        password = raw_input("Password: ").strip()
        authenticate(sys.argv[1], password)

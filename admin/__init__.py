"""
This module is just a dummy module that serves to redirect things in the /admin
path to things in the tutoring and request modules. This is kind of a hack to
get the stuff in that section of the navigation bar to actually have that
menu header selected in those urls. Currently this doesn't cause any URL
conflicts with anything in the Django admin, but it might be wise to change the
base url to something like /admin1 or something less ugly anyway, just to be on
the safe side.
"""
#!/usr/bin/env python
import hkn_settings

print "Generating model users"
import generate_model_users; generate_model_users.main()
print "Generating privacy settings"
import generate_privacy_settings; generate_privacy_settings.main()
print "Generating new event dates"
import generate_new_event_dates; generate_new_event_dates.main()
print "Generating random rsvps"
import generate_random_rsvps; generate_random_rsvps.main()
print "Generating event permissions"
import generate_event_permissions; generate_event_permissions.main()


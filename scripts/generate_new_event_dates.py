#!/usr/bin/env python
import hkn_settings
from hkn.event.models import *
import datetime

td = datetime.timedelta(days=120)
def main():
    for event in Event.objects.all():
        event.start_time = event.start_time + td
        event.end_time = event.end_time  + td
        event.save()

if __name__ == "__main__":
    main()

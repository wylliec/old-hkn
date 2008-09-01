#!/usr/bin/env python
import os
import setup_settings

from course.models import *

def main():
    for k in Klass.objects.all():
        k.instructor_names
        k.save()

if __name__ == "__main__":
    main()

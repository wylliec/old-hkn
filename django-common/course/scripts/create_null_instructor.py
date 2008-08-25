#!/usr/bin/env python
import setup_settings
from course.models import *

def main():
    Instructor.objects.create(first="Instructor", last="Unknown", home_department=Department.objects.ft_query("CS")[0], exams_preference=0)

if __name__ == "__main__":
    main()

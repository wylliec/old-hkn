#!/usr/bin/env python
import os, os.path, glob

def import_all(path):
    import setup_settings
    cd = setup_settings.get_scripts_directory()

    os.chdir(cd)

    os.system('python import_departments.py')
    os.system('python import_courses.py')
    os.system('python import_instructors.py')
    os.system('cd data/klass/xml && tar xfj schedules.tbz && cd ../..')
    
    klassFiles = glob.glob(os.path.join(cd, "data/klass/xml/*.xml"))
    for klassFile in klassFiles:
        os.system('python import_klasses.py "%s"' % klassFile)
    os.system('python merge_instructors.py')
    os.system('python manual_merge.py')
    os.system('python create_null_instructor.py')


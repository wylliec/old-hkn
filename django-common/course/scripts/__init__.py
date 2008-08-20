#!/usr/bin/env python
import os

def import_all(path):
    import setup_settings
    setup_settings.PATH = path
    setup_settings.setup()

    import import_seasons; import_seasons.main()
    import import_departments; import_departments.main()
    import import_courses; import_courses.main()
    import import_instructors; import_instructors.main()

    os.system('cd data/klass/xml && tar xvfj schedules.tbz && cd ../..')

    import import_klasses; import_klasses.main()

    import merge_instructors; merge_instructors.main()
    import manual_merge; manual_merge.main()


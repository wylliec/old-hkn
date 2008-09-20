#!/usr/bin/env python
import setup_settings

from resume.models import *

def group_resumes(resumes):
    def key(resume):
        return str(resume.person.extendedinfo.grad_semester.year)
    r = {}
    for resume in resumes:
        if key(resume) not in r:
            r[key(resume)] = []
        r[key(resume)].append(resume)
    return r

def export_resumes(resumes, export_dir):
    try:
        os.makedirs(export_dir)
    except OSError:
        pass

    for key, r in resumes.items():
        dir = os.path.join(export_dir, key)
        try:
            os.mkdir(dir)
        except OSError:
            pass

        for resume in r:
            filename = os.path.join(dir, "%s, %s%s" % (resume.person.last_name, resume.person.first_name, os.path.splitext(resume.resume.name)[1]))
            f = file(filename, "w")
            f.write(resume.resume.read())
            f.close()

def main(export_dir):
    resumes = group_resumes(Resume.objects.for_current_semester())
    export_resumes(resumes, export_dir)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])

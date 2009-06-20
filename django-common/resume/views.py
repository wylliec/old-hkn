from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from nice_types import semester
from hkn.info.models import Person
from resume.models import *
from resume.forms import ResumeForm

import os, os.path, tempfile, glob, datetime, hashlib

@login_required
def upload(request):
    if request.POST:
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user.person)
            request.user.message_set.create(message="Resume uploaded successfully")
            form = ResumeForm()
    else:
        form = ResumeForm()
    form.bind_person(request.user.person)
    
    return render_to_response("resume/upload.html", {'form' : form, 'person' : request.user.person}, context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def missing(request):
    d = {}
    d['officers'] = set(Person.officers.all()) - set([r.person for r in Resume.objects.filter(submitted__gte = semester.current_semester().start_date)])
    d['candidates'] = set(Person.candidates.all()) - set([r.person for r in Resume.objects.filter(submitted__gte = semester.current_semester().start_date)])
    return render_to_response("resume/missing.html", d, context_instance=RequestContext(request))

from collections import defaultdict
def group_resumes(resumes):
    current_semester = semester.current_semester()
    def key(resume):
        s = resume.person.extendedinfo.grad_semester
        if s.year < current_semester.year:
            return ("grads", "Graduates")
        else:
            yr = str(resume.person.extendedinfo.grad_semester.year)
            return (yr, "Class of " + yr)
    r = defaultdict(list)
    for resume in resumes:
        k = key(resume)
        name = "%s, %s" % (resume.person.last_name.title(), resume.person.first_name.title())
        r[k].append((name, resume))
    for k in r:
        r[k].sort()
    r = r.items()
    # r looks like 
    # [(('2009', "Class of 2009"), [("Zarka, Hisham", <Resume object>), ...]), ...]

    def key(a):
        try:
            return int(a[0][0])
        except ValueError:      # when a[0][0] is 'grads'
            return 0            # put it at the top of the list
    r.sort(key=key)
    return r


LATEX_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "latex")

@user_passes_test(lambda u: u.is_staff)
def generate_book(request):
    from hkn.info.models import Person, Position, Officership
    from django.template import Template, Context

    templates = {}
    for t in ("indrel_letter.tex", "table_of_contents.tex"):
        f = open(os.path.join(LATEX_DIR, t),"r")
        templates[t] = Template(f.read())
        f.close()

    resumes = group_resumes(Resume.objects.filter(resume__endswith="pdf").for_current_semester())
    resume_yrs = [r[0][0] for r in resumes]
    current_semester = semester.current_semester()

    indrel_officers = [o.person.name for o in Officership.objects.for_current_semester().filter(position=Position.objects.get(short_name="indrel"))]
    indrel_officers.sort()

    letter_context = Context({'indrel_officers' : indrel_officers})
    table_context = Context({'resumes' : resumes})
    letter = templates['indrel_letter.tex'].render(letter_context)
    table = templates['table_of_contents.tex'].render(table_context)

    tempdir = tempfile.mkdtemp()
    f = open(os.path.join(tempdir, "indrel_letter.tex"), "w")
    f.write(letter)
    f.close()

    f = open(os.path.join(tempdir, "table_of_contents.tex"), "w")
    f.write(table)
    f.close()
    
    os.system("""cp -R %s '%s'""" % (os.path.join(LATEX_DIR, "skeleton", "*"), tempdir))

    w = open(os.path.join(tempdir, "ResumeBookISO", "Welcome.html"), "r")
    wt = w.read()
    w.close()

    w = open(os.path.join(tempdir, "ResumeBookISO", "Welcome.html"), "w")
    w.write(wt.replace("SEMESTER", current_semester.verbose_description()))
    w.close()

    for clazz, names in resumes:
        d = os.path.join(tempdir, "ResumeBookISO", "Resumes", clazz[0])
        os.system("mkdir -p '%s'" % d)
        for name,  resume in names:
            os.system("cp '%s' '%s'" % (resume.resume.path, os.path.join(d, name + os.path.splitext(resume.resume.path)[1])))

    cmds = []
    rtitles = []
    for yr in resume_yrs:
        os.system("cp '%s' '%s'" % (os.path.join(LATEX_DIR, "titles", "title_%s.pdf" % yr), tempdir))
        rtitles.append(os.path.join(tempdir, "title_%s.pdf" % yr))
        rtitles.append(os.path.join(tempdir, "resumes_%s.pdf" % yr))
        cmds.append( ("pdftk %s cat output %s" % (os.path.join(tempdir, "ResumeBookISO", "Resumes", yr, "*.pdf"),
                                            os.path.join(tempdir, "resumes_%s.pdf" % yr))) )

    os.system("find %s -name \*doc -print0 | xargs -0 zip %s" % (tempdir, os.path.join(tempdir, "docs.zip")))

    f = open(os.path.join(tempdir, "compile_book.sh"), "w")
    f.write("""#!/bin/sh\n%s""" % "\n".join(cmds))
    f.write("\ncd %s && pdflatex '%s'" % (tempdir, os.path.join(tempdir, "indrel_letter.tex")))
    f.write("\ncd %s && pdflatex '%s'" % (tempdir, os.path.join(tempdir, "table_of_contents.tex")))
    f.write("\ncd %s && pdftk cover.pdf indrel_letter.pdf table_of_contents.pdf %s cat output %s" % (tempdir, ' '.join(rtitles), os.path.join(tempdir, "ResumeBookISO", "HKNResumeBook.pdf")))
    f.write("\ncd %s && genisoimage -V 'HKN Resume Book' -o %s -R -J %s" % (tempdir, os.path.join(tempdir, "HKNResumeBook.iso"), os.path.join(tempdir, "ResumeBookISO")))
    f.close()

    os.system("sh '%s'" % (os.path.join(tempdir, "compile_book.sh")))
    try:
        os.mkdir(os.path.join(settings.MEDIA_ROOT, "resumebooks"))
    except OSError:
        pass

    temp = hashlib.sha224(os.path.basename(tempdir)).hexdigest()
    os.system("cp %s '%s'" % (os.path.join(tempdir, "HKNResumeBook.iso"), os.path.join(settings.MEDIA_ROOT, "resumebooks", "%s-HKNResumeBook.iso" % temp)))
    os.system("cp %s '%s'" % (os.path.join(tempdir, "ResumeBookISO", "HKNResumeBook.pdf"), os.path.join(settings.MEDIA_ROOT, "resumebooks", "%s-HKNResumeBook.pdf" % temp)))

    return HttpResponseRedirect(reverse('resume-list-books'))

@user_passes_test(lambda u: u.is_staff)
def delete_book(request):
    if request.POST and 'hash' in request.POST:
        hash = request.POST['hash']
        loc = os.path.join(settings.MEDIA_ROOT, "resumebooks", "%sHKNResumeBook." % hash)
        try:
            os.remove(loc + "pdf")
            os.remove(loc + "iso")
        except OSError:
            request.user.message_set.create("Problem deleting book")
            pass
    return HttpResponseRedirect(reverse('resume-list-books'))

@user_passes_test(lambda u: u.is_staff)
def list_books(request):
    pdfs = [(os.path.basename(p).replace("HKNResumeBook.pdf", ""), datetime.datetime.fromtimestamp(os.stat(p).st_ctime)) for p in glob.glob(os.path.join(settings.MEDIA_ROOT, "resumebooks", "*.pdf"))]
    pdfs.sort(key = lambda p: p[1])
    pdfs.reverse()

    num_docs = Resume.objects.for_current_semester().filter(resume__endswith=".doc").count()

    return render_to_response("resume/list_books.html", {'pdfs' : pdfs, 'num_docs' : num_docs}, context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def replace_doc(request):
    if request.POST:
        resume = get_object_or_404(Resume, pk=request.POST.get('resume', -1))
        resume.save_resume_file(request.FILES['resume_file'].read(), os.path.splitext(request.FILES['resume_file'].name)[1])
        request.user.message_set.create(message="Uploaded successfully")
    else:
        request.user.message_set.create(message="Upload failed")
    return HttpResponseRedirect(reverse('resume-list-docs'))

@user_passes_test(lambda u: u.is_staff)
def table_of_contents(request, docs_only=False):
    if docs_only:
        resumes = Resume.objects.for_current_semester().filter(resume__endswith=".doc")
    else:
        resumes = Resume.objects.for_current_semester()
    d = {}
    d['resumes'] = group_resumes(resumes)
    d['docs_only'] = docs_only
    return render_to_response("resume/table_of_contents.html", d, context_instance=RequestContext(request))

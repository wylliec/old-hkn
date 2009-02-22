import os.path, datetime
from django import forms
from nice_types import semester

from hkn.cand.models import EligibilityListEntry, CandidateApplication
from course.models import Course

def application_form_for_candidate(person, data=None):
    if not data:
        data = {}
        data['phone']               = person.phone
        data['local_addr']          = person.extendedinfo.local_addr
        data['perm_addr']           = person.extendedinfo.perm_addr
        data['release_information'] = person.candidateinfo.candidateapplication.release_information
        if len(person.candidateinfo.candidateapplication.committees) > 1:
            data['committee_act']       = 1+person.candidateinfo.candidateapplication.committees.index('act')
            data['committee_bridge']    = 1+person.candidateinfo.candidateapplication.committees.index('bridge')
            data['committee_compserv']  = 1+person.candidateinfo.candidateapplication.committees.index('compserv')
            data['committee_examfiles'] = 1+person.candidateinfo.candidateapplication.committees.index('examfiles')
            data['committee_indrel']    = 1+person.candidateinfo.candidateapplication.committees.index('indrel')
            data['committee_pub']       = 1+person.candidateinfo.candidateapplication.committees.index('pub')
            data['committee_studrel']   = 1+person.candidateinfo.candidateapplication.committees.index('studrel')
            data['committee_tutor']     = 1+person.candidateinfo.candidateapplication.committees.index('tutor')
            data['question_activities'] = person.candidateinfo.candidateapplication.questions[0][1]
        print "\n\n\n\n\n\n\n\n\n\n\n\n"
        print data.keys()
    
    
    form = CandidateApplicationForm(person, data)
    return form

class CandidateApplicationForm(forms.Form):

    QUESTIONS = (
                    ('activities', 'What activities would you like to see HKN do this semester?'),
    )

    aim_sn          = forms.CharField(  max_length=30,
                                        widget=forms.TextInput(),
                                        label=(u'AIM screen name (optional)'),
                                        required=False,
                                        )

    local_addr      = forms.CharField(  max_length=100,
                                        widget=forms.TextInput(),
                                        label=(u'Your Local (Berkeley) Address'),
                                        )

    perm_addr       = forms.CharField(  max_length=100,
                                        widget=forms.TextInput(),
                                        label=(u'Your Permanent Address'),
                                        )

    phone           = forms.CharField(max_length=30)
    grad_semester = semester.SemesterSplitFormField(help_text="Your intended graduation semester", initial=semester.Semester(season_name="Spring", year=datetime.date.today().year + 2))
    #tech_courses    = forms.CharField(max_length=2000, label="Current Tech Courses", help_text="a comma-separated list of your technical classes, such as: 'CS 61A, MATH 53, EE 20N'")

    release_information = forms.BooleanField(required=False, label="Release information to other candidates", help_text="Check this box if you would like to release your information to other candidates.")

    RANKING_CHOICES = [(str(x), x) for x in range(1, 9)]

    committee_act = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Activities Committee")
    committee_bridge = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Bridge Committee")
    committee_compserv = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for CompServ Committee")
    committee_examfiles = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for ExamFiles Committee")
    committee_indrel = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Indrel Committee")
    committee_pub = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Pub Committee")
    committee_studrel = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for StudRel Committee")
    committee_tutor = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Tutoring Committee")

    def __init__(self, person, *args, **kwargs):
        super(CandidateApplicationForm, self).__init__(*args, **kwargs)
        self.person = person
        for qid, prompt in CandidateApplicationForm.QUESTIONS:
            field = forms.CharField(label=prompt, widget=forms.Textarea)
            self.fields["question_" + qid] = field

    '''
    def clean_tech_courses(self):
        courses = [c.strip() for c in self.cleaned_data['tech_courses'].split(",")]
        clean_courses = []
        for course in courses:
            qr = Course.objects.query_exact(*Course.objects.parse_query(course))
            if len(qr) == 0:
                raise forms.ValidationError('No matches for course %s!' % course) 
            elif len(qr) > 1:
                raise forms.ValidationError('Too many matches for course %s!' % course) 
            clean_courses.append(qr[0])
        self.cleaned_data['tech_courses'] = clean_courses
        return self.cleaned_data['tech_courses']
    '''

    def bind_person(self, person):
        if  person.extendedinfo.grad_semester:
            self.fields['grad_semester'].initial = person.extendedinfo.grad_semester

    def clean_phone_number(self):
        self.cleaned_data['phone_number'] = filter(lambda char: char in string.digits, self.cleaned_data['phone_number'])
        if len(self.cleaned_data['phone_number']) < 10:
            raise forms.ValidationError("Ensure your phone number %s is longer than 10 digits" % self.cleaned_data['phone_number'])
        return self.cleaned_data

    def clean(self):
        committee_keys = filter(lambda key: key.startswith("committee_"), self.cleaned_data.keys())
        committees = [None] * len(CandidateApplicationForm.RANKING_CHOICES)
        for committee_key in committee_keys:
            committees[int(self.cleaned_data[committee_key])-1] = committee_key.replace("committee_", "")
        if None in committees:
            raise forms.ValidationError('Please provide a valid committee ranking')
        self.cleaned_data['committees'] = committees

        answers = []
        for qid, prompt in CandidateApplicationForm.QUESTIONS:
            key = 'question_' + qid
            answers.append((qid, prompt, self.cleaned_data.get(key, "")))
        self.cleaned_data['questions'] = tuple(answers)

        for key in self.data.keys():
            print "\n\n\n\n\n\n"
            print key
            if not key in self.cleaned_data.keys():
                self.cleaned_data[key] = self.data[key]

        return self.cleaned_data
    
    def save_for_person(self):
        
        self.person.phone   = self.cleaned_data['phone']
        self.person.save()

        extendedinfo = self.person.extendedinfo
        extendedinfo.local_addr     = self.cleaned_data['local_addr']         
        extendedinfo.perm_addr      = self.cleaned_data['perm_addr']          
        extendedinfo.grad_semester  = self.cleaned_data['grad_semester']      
        #extendedinfo.tech_courses   = self.cleaned_data['tech_courses']       
        extendedinfo.save()

        candidateapplication = self.person.candidateinfo.candidateapplication
        candidateapplication.release_information    = self.cleaned_data['release_information']
        candidateapplication.committees             = self.cleaned_data['committees']
        candidateapplication.questions              = self.cleaned_data['questions']
        candidateapplication.save()

class EligibilityListForm(forms.Form):
    eligibility_list = forms.CharField(widget=forms.Textarea)

    def clean_eligibility_list(self):
        if self.cleaned_data.has_key('eligibility_list') and len(self.cleaned_data['eligibility_list']) > 0:
            try:
                self.cleaned_data['eligibility_dicts'] = []
                for line in self.cleaned_data['eligibility_list'].split("\n"):
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    tokens = line.split("\t")
                    names = ('last_name', 'first_name', 'middle_initial', 'major', 'email_address', 'local_street1', 'local_street2', 'local_city', 'local_state', 'local_zip', 'class_level')
                    kwargs = dict(zip(names, tokens))
                    kwargs['semester'] = semester.current_semester()
                    if kwargs['last_name'] == "Last Name":
                        continue
                    self.cleaned_data['eligibility_dicts'].append(kwargs)
            except Exception, e:
                    raise forms.ValidationError("Error parsing eligibility list: %s" % str(e))
        return self.cleaned_data


    def save_list(self):
        num_created = num_existed = 0
        for kwargs in self.cleaned_data['eligibility_dicts']:
            entry, created = EligibilityListEntry.objects.get_or_create(**kwargs)
            if created:
                num_created += 1
            else:
                num_existed += 1
        return (num_created, num_existed)

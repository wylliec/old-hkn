"""
Forms and validation code for user registration.

"""


from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from nice_types import semester

from registration.models import RegistrationProfile
from course.models import Course

import re, string

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = { 'class': 'required' }


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should either preserve the base ``save()`` or implement
    a ``save()`` which accepts the ``profile_callback`` keyword
    argument and passes it through to
    ``RegistrationProfile.objects.create_inactive_user()``.
    
    """
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u'First Name'))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u'Last Name'))
    
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u'Username'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u'Email Address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Password (again)'))
    hkn_member = forms.BooleanField(required=False, label="HKN Member", help_text="Check this box if you are a member of HKN")
    
    USERNAME_RE = re.compile("[A-Za-z0-9_]")
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        if not RegistrationForm.USERNAME_RE.search(self.cleaned_data['username']):
            raise forms.ValidationError(_(u'Usernames can only contain letters, numbers and underscores'))
        
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        #if email_domain not in ('berkeley.edu',):
        #    raise forms.ValidationError(_(u'Please provide an @berkeley.edu email address.'))        
        #if User.objects.filter(email__iexact=self.cleaned_data['email']):
            #raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
        return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'You must type the same password each time'))
        return self.cleaned_data
    
    def save(self, profile_callback=None):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.
        
        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(first_name=self.cleaned_data['first_name'],
                                                                    last_name=self.cleaned_data['last_name'],
                                                                    username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    hkn_member=self.cleaned_data['hkn_member'],
                                                                    profile_callback=profile_callback)
        return new_user


# we should refactor so there isn't so much code dup --hzarka
class CandidateRegistrationForm(forms.Form):
    QUESTIONS = (
            ('activities', 'What activities would you like to see HKN do this semester?'),
            ('crazy', "What's the craziest thing you've ever done?"),
            ('unique', "What's something unique about you?"),
            ('nerdy', "If you were a programming language or filter, what would you be and why?"),
    )

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u'First Name'))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u'Last Name'))
    
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u'Username'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u'Email Address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Password (again)'))

    phone_number = forms.CharField(max_length=30)
    grad_semester = semester.SemesterSplitFormField()
    tech_courses = forms.CharField(max_length=2000, label="Current Tech Courses", help_text="a comma-separated list of your technical classes, such as: 'CS 61A, MATH 53, EE 20N'")

    RANKING_CHOICES = [(str(x), x) for x in range(1, 9)]

    committee_act = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Activities Committee")
    committee_bridge = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Bridge Committee")
    committee_compserv = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for CompServ Committee")
    committee_examfiles = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for ExamFiles Committee")
    committee_indrel = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Indrel Committee")
    committee_pub = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Pub Committee")
    committee_studrel = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for StudRel Committee")
    committee_tutor = forms.ChoiceField(choices=RANKING_CHOICES, label="Preference for Tutoring Committee")

    question_activities = forms.CharField(label="What activities would you like to see HKN do this semester?", widget=forms.Textarea)
    question_unique = forms.CharField(label="What's something unique about you?", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(CandidateRegistrationForm, self).__init__(*args, **kwargs)
        for qid, prompt in CandidateRegistrationForm.QUESTIONS:
            field = forms.CharField(label=prompt, widget=forms.Textarea)
            self.fields["question_" + qid] = field

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
            
    
    USERNAME_RE = re.compile("[A-Za-z0-9_]")
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        if not RegistrationForm.USERNAME_RE.search(self.cleaned_data['username']):
            raise forms.ValidationError(_(u'Usernames can only contain letters, numbers and underscores'))
        
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        #if email_domain not in ('berkeley.edu',):
        #    raise forms.ValidationError(_(u'Please provide an @berkeley.edu email address.'))        
        #if User.objects.filter(email__iexact=self.cleaned_data['email']):
            #raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
        return self.cleaned_data['email']

    def clean_phone_number(self):
        self.cleaned_data['phone_number'] = filter(lambda char: char in string.digits, self.cleaned_data['phone_number'])
        if len(self.cleaned_data['phone_number']) < 10:
            raise forms.ValidationError("Ensure your phone number %s is longer than 10 digits" % self.cleaned_data['phone_number'])
        return self.cleaned_data

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'You must type the same password each time'))

        committee_keys = filter(lambda key: key.startswith("committee_"), self.cleaned_data.keys())
        committees = [None] * len(CandidateRegistrationForm.RANKING_CHOICES)
        for committee_key in committee_keys:
            committees[int(self.cleaned_data[committee_key])-1] = committee_key.replace("committee_", "")
        if None in committees:
            raise forms.ValidationError('Please provide a valid committee ranking')
        self.cleaned_data['committees'] = committees

        answers = []
        for qid, prompt in CandidateRegistrationForm.QUESTIONS:
            key = 'question_' + qid
            answers.append((qid, prompt, self.cleaned_data[key]))
        self.cleaned_data['questions'] = tuple(answers)

        return self.cleaned_data

    def bind_entry(self, entry):
        self.entry = entry
        self.fields['first_name'].initial = entry.first_name
        self.fields['last_name'].initial = entry.last_name
        self.fields['email'].initial = entry.email_address
        self.fields['username'].initial = entry.email_address.split("@")[0]
    
    def save(self):
        new_user = RegistrationProfile.objects.create_candidate_user(self.entry,
                                                                    first_name=self.cleaned_data['first_name'],
                                                                    last_name=self.cleaned_data['last_name'],
                                                                    username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    phone_number=self.cleaned_data['phone_number'],
                                                                    grad_semester=self.cleaned_data['grad_semester'],
                                                                    courses=self.cleaned_data['tech_courses'],
                                                                    committees=self.cleaned_data['committees'],
                                                                    questions=self.cleaned_data['questions'],
                                                                    transfer_college="")
        return new_user


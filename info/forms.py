from django import forms
from django.core.files.base import ContentFile
import os.path
from hkn.info.constants import MEMBER_TYPE

def profile_form_for_person(person, data=None):
    clazz = ProfileForm
    if person.member_type >= MEMBER_TYPE.FOGIE:
        clazz = OfficerProfileForm
    
    if not data:
        data = {}
        data['email'] = person.email
        data['phone'] = person.phone
    
        for key in filter(lambda key: key.startswith("privacy_"), clazz.__dict__['base_fields'].keys()):
            data[key] = person.privacy.get(key[8:], MEMBER_TYPE.REGISTERED)
    
    form = clazz(person, data)
    return form

class PrivacySelectField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = ((MEMBER_TYPE.REGISTERED, 'Registered users'),
                             (MEMBER_TYPE.CANDIDATE, 'Current HKN candidates'),
                             (MEMBER_TYPE.MEMBER, 'HKN Members'),
                             (MEMBER_TYPE.FOGIE, 'HKN Officers'),
                             (1000, 'Nobody'),                             
                             )
        super(PrivacySelectField, self).__init__(*args, **kwargs)
        
    def clean(self, value):
        try:
            value = int(value)
        except:
            raise forms.ValidationError("Privacy field value incorrect")
        return value

class ProfileForm(forms.Form):
    email = forms.CharField(label="Contact Email")
    phone = forms.CharField(label="Contact Phone", required=False)
    current_password = forms.CharField(required=False, widget=forms.PasswordInput)
    new_password = forms.CharField(required=False, widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(required=False, widget=forms.PasswordInput)

    privacy_email = PrivacySelectField(label="Email Privacy", help_text="who should be able to view your email address")    
    privacy_phone = PrivacySelectField(label="Phone Privacy", help_text="who should be able to view your phone number")    
    privacy_profile_picture = PrivacySelectField(label="Photo Privacy", help_text="who should be able to view your profile picture")        
        
    def __init__(self, person, *args, **kwargs):
        self.person = person
        super(ProfileForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        if self.cleaned_data.has_key('new_password'):
            if not self.cleaned_data.has_key('confirm_new_password'):
                raise forms.ValidationError('Please confirm your password change')
            if self.cleaned_data['new_password'] != self.cleaned_data['confirm_new_password']:
                raise forms.ValidationError('Passwords do not match')        
        return self.cleaned_data
    
    def clean_current_password(self):
        if self.cleaned_data.has_key('current_password') and len(self.cleaned_data['current_password']) > 0:
            if not self.person.check_password(self.cleaned_data['current_password']):
                raise forms.ValidationError('Current password is not correct')
        return self.cleaned_data
            
    def save_for_person(self):
        self.person.email = self.cleaned_data['email']
        self.person.phone = self.cleaned_data['phone']
        
        privacy_keys = filter(lambda key: key.startswith("privacy_"), self.cleaned_data.keys())
        for key in privacy_keys:
            self.person.privacy[key[8:]] = self.cleaned_data[key]
        
        if len(self.cleaned_data['current_password']) > 0:
            self.person.set_password(self.cleaned_data['new_password'])
        self.person.save()
    
class OfficerProfileForm(ProfileForm):
    privacy_officer_picture = PrivacySelectField(label="Officer Photo Privacy", help_text="who should be able to view your officer profile picture")        
    
class ChangePictureForm(forms.Form):
    profile_picture = forms.ImageField()
    
    def save_for_person(self, person):
        uploaded_file = self.cleaned_data['profile_picture']
        person.profile_picture.save(person.generate_filename("%s%s" % (person.username, os.path.splitext(uploaded_file.name)[1])), ContentFile(uploaded_file.read()))
        person.save()
        
        

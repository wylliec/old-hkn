from django import forms
import os.path
from nice_types import semester

from hkn.cand.models import EligibilityListEntry

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
        

from django.db import models
from django.contrib.localflavor.us import models as us_models
import os.path

class CompanyAndContactForm(models.Model):
    name = models.CharField(max_length=100, verbose_name="Company Name")
    address1 = models.CharField(max_length=100, verbose_name="Address 1")
    addesss2 = models.CharField(max_length=100, verbose_name="Address 2")
    city = models.CharField(max_length=100, verbose_name="City")
    state = us_models.USStateField(default="CA")
    zip = models.IntegerField(verbose_name="Zip Code")

    contactname = models.CharField(max_length=100, verbose_name="Contact Name")
    contacttitle = models.CharField(max_length=100, verbose_name="Contact Title")
    contactemail = models.EmailField(verbose_name="Contact Email")

    class Meta:
        abstract = True

class InfosessionRegistration(CompanyAndContactForm):
    dates = models.CharField(max_length=100, verbose_name="Preferred Dates")
    advertise = models.CharField(max_length=100, verbose_name="Advertise", help_text="Preferred advertising methods")
    comments = models.TextField(max_length=100, verbose_name="Additional Comments")

class ResumeBookOrder(CompanyAndContactForm):
    pass

from hkn.indrel.admin import *

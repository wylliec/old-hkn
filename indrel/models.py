from django.db import models
from django.contrib.localflavor.us import models as us_models
import os.path

class InfosessionRegistration(models.Model):
    name = models.CharField(max_length=100, verbose_name="Company Name")
    address1 = models.CharField(max_length=100, verbose_name="Address 1")
    addesss2 = models.CharField(max_length=100, verbose_name="Address 2")
    city = models.CharField(max_length=100, verbose_name="City")
    state = us_models.USStateField(default="CA")
    zip = models.IntegerField(verbose_name="Zip Code")

    primaryname = models.CharField(max_length=100, verbose_name="Primary Contact Name")
    primarytitle = models.CharField(max_length=100, verbose_name="Primary Contact Title")
    primaryemail = models.EmailField(verbose_name="Primary Contact Email")

    alternatename = models.CharField(max_length=100, verbose_name="Alternate Contact Name")
    alternatetitle = models.CharField(max_length=100, verbose_name="Alternate Contact Title")
    alternateemail = models.EmailField(verbose_name="Alternate Contact Email")

    dates = models.CharField(max_length=100, verbose_name="Preferred Dates")
    advertise = models.CharField(max_length=100, verbose_name="Advertise")
    comments = models.CharField(max_length=100, )

from hkn.indrel.admin import *

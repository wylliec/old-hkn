from django.db import models

from hkn.info.models import *
# Create your models here.

class SMSInfo(models.Model):
    # 1-1 correspondence 
    person = models.OneToOneField(Person)

    # has this person activated SMS?
    activated = models.BooleanField(default = False)

    # the person's passcode
    passcode = models.CharField(max_length = 20, default = "")

    # the person's carrier
    carrier = models.CharField(max_length = 50)

    # the person's usual phone-email address
    # like 55555555555@vtext.com
    phone_email = models.CharField(max_length=70)

    # cache the response to their last query so we can page responses
    cached_response = models.TextField()

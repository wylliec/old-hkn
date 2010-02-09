import datetime
import random
import re
import hashlib
import logging

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Permission
from django.contrib.sites.models import Site

from hkn.info.models import Person
from hkn.info.constants import MEMBER_TYPE
from hkn.cand.models import CandidateInfo, CandidateApplication

from nice_types import semester

from hkn.main.property import PROPERTIES

import request

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.
    
    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.
    
    """
    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.
        
        If the key is valid and has not expired, return the ``User``
        after activating.
        
        If the key is not valid or has expired, return ``False``.
        
        If the key is valid but the ``User`` is already active,
        return ``False``.
        
        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string ``ALREADY_ACTIVATED`` after successful
        activation.
        
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                logging.getLogger('special.actions').info("Activation attempt failed with key %s" % activation_key)
                return False
            if not profile.activation_key_expired():
                logging.getLogger('special.actions').info("%s activated account" % profile.user.username)
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = "ALREADY_ACTIVATED"
                if profile.hkn_member:
                    profile.request_confirmation()
                profile.save()
                return user
            else:
                logging.getLogger('special.actions').info("%s failed account activation with expired key %s" % (profile.user.username, profile.activation_key))
        return False

    def create_candidate_user(self, entry, first_name, last_name, username, password, email,
                             phone_number, grad_semester, transfer_college, courses, committees, questions):
        #new_person = self.create_inactive_user(first_name, last_name, username, password, email, False, send_email=True)

        new_person = self.create_inactive_user(first_name, last_name, username, password, email, False, send_email=False)
        new_person.is_active = True

        new_person.phone_number = phone_number
        new_person.realfirst = entry.first_name
        new_person.school_email = entry.email_address
        new_person.member_type = MEMBER_TYPE.CANDIDATE
        new_person.save()
        new_person.extendedinfo.grad_semester = grad_semester
        new_person.extendedinfo.save()
        new_person.extendedinfo.current_courses = courses
        new_person.extendedinfo.save()

        candidateinfo = CandidateInfo.objects.create(person=new_person, candidate_semester=semester.current_semester(), candidate_committee=None, initiated=False, initiation_comment="", candidate_picture=None)
        
        candidateapp = CandidateApplication.objects.create(entry=entry, candidateinfo=candidateinfo, transfer_college=transfer_college, committees=committees, questions=questions)

        return new_person
        
    
    def create_inactive_user(self, first_name, last_name, username, password, email, hkn_member, hkn_candidate,
                             send_email=True, profile_callback=None):
        """
        Create a new, inactive ``User``, generates a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.
        
        To disable the email, call with ``send_email=False``.
        
        To enable creation of a custom user profile along with the
        ``User`` (e.g., the model specified in the
        ``AUTH_PROFILE_MODULE`` setting), define a function which
        knows how to create and save an instance of that model with
        appropriate default values, and pass it as the keyword
        argument ``profile_callback``. This function should accept one
        keyword argument:

        ``user``
            The ``User`` to relate the profile to.
        """
        new_person = Person.objects.create_person(first_name, last_name, username, email, MEMBER_TYPE.REGISTERED, password=password)
        new_person.is_active = False
        if hkn_candidate:
            new_person.member_type = MEMBER_TYPE.CANDIDATE
            candidateinfo = CandidateInfo.objects.create(person=new_person, candidate_semester=semester.current_semester(), candidate_committee=None, initiated=False, initiation_comment="", candidate_picture=None)
            candidateapp = CandidateApplication.objects.create(candidateinfo=candidateinfo, transfer_college=None, committees={}, questions={})
            
        new_person.save()

        
        registration_profile = self.create_profile(new_person, hkn_member)
        logging.getLogger('special.actions').info("%s [%s] registered for account with email %s and key %s" % (new_person.username, new_person.name, new_person.email, registration_profile.activation_key))
        
        if send_email:
            from django.core.mail import send_mail
            current_site = Site.objects.get_current()
            
            subject = render_to_string('registration/activation_email_subject.txt',
                                       { 'site': current_site })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            
            message = render_to_string('registration/activation_email.txt',
                                       { 'activation_key': registration_profile.activation_key,
                                         'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                         'person' : new_person,
                                         'vp' : PROPERTIES.vp,
                                         'site': current_site })
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_person.email])
        return new_person
    
    def create_profile(self, user, hkn_member):
        """
        Create a ``RegistrationProfile`` for a given
        ``User``, and return the ``RegistrationProfile``.
        
        The activation key for the ``RegistrationProfile`` will be a
        SHA1 hash, generated from a combination of the ``User``'s
        username and a random salt.
        
        """
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt+user.username).hexdigest()
        return self.create(user=user, hkn_member=hkn_member,
                           activation_key=activation_key)
        
    def delete_expired_users(self):
        """
        Remove expired instances of ``RegistrationProfile`` and their
        associated ``User``s.
        
        Accounts to be deleted are identified by searching for
        instances of ``RegistrationProfile`` with expired activation
        keys, and then checking to see if their associated ``User``
        instances have the field ``is_active`` set to ``False``; any
        ``User`` who is both inactive and has an expired activation
        key will be deleted.
        
        It is recommended that this method be executed regularly as
        part of your routine site maintenance; the file
        ``bin/delete_expired_users.py`` in this application provides a
        standalone script, suitable for use as a cron job, which will
        call this method.
        
        Regularly clearing out accounts which have never been
        activated serves two useful purposes:
        
        1. It alleviates the ocasional need to reset a
           ``RegistrationProfile`` and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.
        
        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those usernames to anyone else); since
           those accounts will be deleted, the usernames will become
           available for use again.
        
        If you have a troublesome ``User`` and wish to disable their
        account while keeping it in the database, simply delete the
        associated ``RegistrationProfile``; an inactive ``User`` which
        does not have an associated ``RegistrationProfile`` will not
        be deleted.
        
        """
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()


class RegistrationProfile(models.Model):
    """
    A simple profile which stores an activation key for use during
    user account registration.
    
    Generally, you will not want to interact directly with instances
    of this model; the provided manager includes methods
    for creating and activating new accounts, as well as for cleaning
    out accounts which have never been activated.
    
    While it is possible to use this model as the value of the
    ``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do
    so. This model's sole purpose is to store data temporarily during
    account registration and activation, and a mechanism for
    automatically creating an instance of a site-specific profile
    model is provided via the ``create_inactive_user`` on
    ``RegistrationManager``.
    
    """
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=40)
    hkn_member = models.BooleanField()
    
    objects = RegistrationManager()
    
    def get_is_member(self):
        return self.user.person.member_type >= MEMBER_TYPE.MEMBER
    
    def set_is_member(self, value):
        person = self.user.person
        if value:
            person.member_type = MEMBER_TYPE.MEMBER
        else:
            person.member_type = MEMBER_TYPE.REGISTERED
        person.save()
        hkn_member = value
        return
    is_member = property(get_is_member, set_is_member)
    
    def request_confirmation(self):
        return request.utils.request_confirmation(self, self.user, Permission.objects.get(codename="group_rsec"))
    
    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
    
    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string ``ALREADY_ACTIVATED``. Re-activating is
           not permitted, and so this method returns ``True`` in this
           case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == "ALREADY_ACTIVATED" or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True

from registration.members import *

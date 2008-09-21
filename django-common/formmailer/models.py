#!/usr/bin/env python
from django.db import models
from django.contrib.auth.models import User, Group
from django.template import Template
from django.template.context import Context, RequestContext

from hkn.main.property import PROPERTIES

from nice_types.db import PickleField

class MailTarget(models.Model):
    group = models.ForeignKey(Group, null=True)
    users = models.CommaSeparatedIntegerField(max_length=3000)
    extra_context = PickleField()

    def get_all_users(self):
        if self.group:
            return self.group.user_set.all()
        return User.objects.filter(id__in = [id.strip() for id in self.users.split(",")])

    @staticmethod
    def create_for_users(users):
        mt = MailTarget()
        mt.users = ",".join([str(u.id) for u in users])
        mt.save()
        return mt

class MailMessage(models.Model):
    title = models.CharField(max_length=50)
    template = models.TextField()

    def __str__(self):
        return self.title

    def render_for_target(self, target, request=None):
        template = Template(self.template)
        context = Context(target.extra_context or {})
        if request:
            context.update(RequestContext(request))
        for user in target.get_all_users():
            context['user'] = user
            context['PROPERTIES'] = PROPERTIES
            yield template.render(context)
    

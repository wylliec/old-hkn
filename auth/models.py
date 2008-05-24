from django.db import models
from django.db import backend, connection, models
import datetime

from hkn.info.models import *


class Permission(models.Model):
    id = models.AutoField(primary_key = True)
    codename = models.CharField('codename', max_length=100)
    name = models.CharField('name', max_length=50)

    def __str__(self):
        return self.name

    class Admin:
        pass
try:
    everyone_permission = Permission.objects.get(codename = "everyone")
except:
    everyone_permission = None

class Group(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField('name', max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission, verbose_name='permissions', related_name = "groups_with")

    def __str__(self):
        return self.name

    class Admin:
        pass

class UserManager(models.Manager):
    def create_user(self, person, username, password):
        "Creates and saves a User with the given username, e-mail and password."
        now = datetime.datetime.now()
        user = self.model(person = person, username = username.lower())
        user.user_created = now
        user.pam_login = False
        user.last_login = now
        user.set_password(password)
        user.force_password_change = False
        user.force_info_update = False
        user.is_superuser = False
        user.is_active = True
        user.save()
        return user

    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])
        

    def isValidUsername(self, username):
        try:
            self.get(username=username)
        except User.DoesNotExist:
            return True
        return False

class User(models.Model):
    person = models.OneToOneField(Person, primary_key = True)
    username = models.CharField(max_length=20, unique = True)
    password = models.CharField(max_length=70)
    pam_login = models.BooleanField()
    last_login = models.DateTimeField()
    user_created = models.DateTimeField()

    force_password_change = models.BooleanField()
    force_info_update = models.BooleanField()
    is_superuser = models.BooleanField()
    is_active = models.BooleanField()

    groups = models.ManyToManyField(Group, verbose_name = 'groups', related_name = "users")
    permissions = models.ManyToManyField(Permission, verbose_name = 'permissions', related_name = "users_with")

    objects = UserManager()

    def __str__(self):
        return self.username

    def set_password(self, password):
#        salt = bcrypt.gensalt()
#        hashed = bcrypt.hashpw(password, salt)
#        self.password = hashed
		self.password = password

    def check_password(self, password):
#        return bcrypt.hashpw(password, self.password[:-30]) == self.password    
    	return password == self.password

    def getFullName(self):	
        return "%s %s" % (self.person.first, self.person.last)

    def get_group_permissions(self):
        "Returns a list of permission strings that this user has through his/her groups."
        if not hasattr(self, '_group_perm_cache'):
            import sets
            cursor = connection.cursor()
            # The SQL below works out to the following, after DB quoting:
            # cursor.execute("""
            #	 SELECT ct."app_label", p."codename"
            #	 FROM "auth_permission" p, "auth_group_permissions" gp, "auth_user_groups" ug, "django_content_type" ct
            #	 WHERE p."id" = gp."permission_id"
            #		 AND gp."group_id" = ug."group_id"
            #		 AND ct."id" = p."content_type_id"
            #		 AND ug."user_id" = %s, [self.id])
            sql = """
                SELECT perm.codename
                FROM auth_permission perm, auth_group_permissions gp, auth_user_groups ug
                WHERE perm.permission_id = gp.permission_id
                    AND gp.group_id = ug.group_id
                    AND ug.user_id = %s""" 
            cursor.execute(sql, [self.id])
            self._group_perm_cache = sets.Set(["%s" % (row[0],) for row in cursor.fetchall()])
        return self._group_perm_cache

    def get_all_permissions(self):
        if not hasattr(self, '_perm_cache'):
            import sets
            if self.is_superuser:
                self._perm_cache = sets.Set(Permission.objects.all())
            else:
                self._perm_cache = sets.Set(["%s" % (p.codename,) for p in self.permissions.select_related()])
                self._perm_cache.update(self.get_group_permissions())
        return self._perm_cache

    def has_perm(self, perm):
        "Returns True if the user has the specified permission."
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return perm in self.get_all_permissions()

    def has_perms(self, perm_list):
        "Returns True if the user has each of the specified permissions."
        for perm in perm_list:
            if not self.has_perm(perm):
                return False
        return True

    def has_module_perms(self, app_label):
        if not self.is_active:
            return False

        if self.is_superuser:
            return True

        return bool(len([p for p in self.get_all_permissions() if p[:p.index('.')] == app_label]))


    def is_anonymous(self):
        return False

    def is_staff(self):
        return self.is_superuser

    def is_authenticated(self):
        return True

    class Admin:
        pass

class AnonymousUser(object):
    id = None
    username = ''

    def __init__(self):
        pass

    def __str__(self):
        return 'AnonymousUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    def _get_groups(self):
        raise NotImplementedError
    groups = property(_get_groups)

    def _get_user_permissions(self):
        raise NotImplementedError
    user_permissions = property(_get_user_permissions)

    def has_perm(self, perm):
        if perm == everyone_permission:
            return True
        return False

    def get_all_permissions(self):
        return [everyone_permission]

    def has_module_perms(self, module):
        return False

    def is_staff(self):
        return False

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

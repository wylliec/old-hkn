from django.contrib.admin.sites import AdminSite
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin

admin_site = AdminSite()
admin_site.register(FlatPage, FlatPageAdmin)


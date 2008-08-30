from django.contrib import admin
from hkn.indrel.models import InfosessionRegistration

class InfosessionRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'primaryname', 'primarytitle', 'primaryemail')

admin.site.register(InfosessionRegistration, InfosessionRegistrationAdmin)

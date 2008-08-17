from django.contrib import admin
from hkn.info.models import Person, Officership


class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'member_type', 'email')
    search_fields = ('last_name', 'first_name', 'username', 'email')
#    filter_horizontal = ('member_type',)
    list_filter = ('member_type',)
    fieldsets = (
        ('Basic Information', {'fields' : ('first_name', 'last_name', 'email', 'member_type')}),
        ('Account Information', {'fields' : ('username', 'password', 'is_staff', 'is_active', 'is_superuser')}),
        ('HKN Information', {'fields' : ()})
        )


class OfficershipAdmin(admin.ModelAdmin):
    pass

admin.site.register(Person, PersonAdmin)
admin.site.register(Officership, OfficershipAdmin)

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin

from hkn.info.models import Person, Officership
from hkn.info.admin import PersonAdmin, OfficershipAdmin

from course.models import Course, Department, Klass
from course.admin import CourseAdmin, DepartmentAdmin, KlassAdmin

from hkn.event.models import Event
from hkn.event.admin import EventAdmin

from hkn.indrel.models import InfosessionRegistration
from hkn.indrel.admin import InfosessionRegistrationAdmin

from photologue.admin import GalleryAdmin, PhotoAdmin, PhotoEffectAdmin, PhotoSizeAdmin, WatermarkAdmin
from photologue.models import Gallery, GalleryUpload, PhotoEffect, PhotoSize, Watermark, Photo

from djangodblog.admin import ErrorAdmin, ErrorBatchAdmin
from djangodblog.models import Error, ErrorBatch

admin_site = AdminSite()
admin_site.register(FlatPage, FlatPageAdmin)

admin_site.register(Person, PersonAdmin)
admin_site.register(Officership, OfficershipAdmin)

admin_site.register(Course, CourseAdmin)
admin_site.register(Department, DepartmentAdmin)
admin_site.register(Klass, KlassAdmin)

admin_site.register(Event, EventAdmin)

admin_site.register(InfosessionRegistration, InfosessionRegistrationAdmin)

admin_site.register(Gallery, GalleryAdmin)
admin_site.register(GalleryUpload)
admin_site.register(Photo, PhotoAdmin)
admin_site.register(PhotoEffect, PhotoEffectAdmin)
admin_site.register(PhotoSize, PhotoSizeAdmin)
admin_site.register(Watermark, WatermarkAdmin)

admin_site.register(Error, ErrorAdmin)
admin_site.register(ErrorBatch, ErrorBatchAdmin)


from hkn.main.models import HKN
class PropertiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
admin_site.register(HKN, PropertiesAdmin)

from registration.models import RegistrationProfile
from registration.admin import RegistrationAdmin
admin_site.register(RegistrationProfile, RegistrationAdmin)

from django.contrib import admin

from hkn.main.admin import admin_site
from models import Course, Department, Klass


class CourseAdmin(admin.ModelAdmin):
    list_display = ('department_abbr', 'number', 'name')

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')
    search_fields = ('name', 'abbr')

class KlassAdmin(admin.ModelAdmin):
    list_display = ('course', 'season', 'year')

admin_site.register(Course, CourseAdmin)
admin_site.register(Klass, KlassAdmin)
admin_site.register(Department, DepartmentAdmin)

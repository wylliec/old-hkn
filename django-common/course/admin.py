from django.contrib import admin
from course.models import Course, Department, Klass


class CourseAdmin(admin.ModelAdmin):
    list_display = ('department_abbr', 'coursenumber', 'name')

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')
    search_fields = ('name', 'abbr')

class KlassAdmin(admin.ModelAdmin):
    list_display = ('course', 'season', 'year')

admin.site.register(Course, CourseAdmin)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Department, DepartmentAdmin)

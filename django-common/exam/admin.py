from django.contrib import admin

from exam.models import Exam
from constants import EXAM_TYPE


class ExamAdmin(admin.ModelAdmin):
    list_display = ('course', lambda exam: exam.klass.semester, Exam.describe_exam_type, 'is_solution', "publishable")
    raw_id_fields = ('klass',)
    search_fields = ('klass__semester', 'course__department_abbr', 'course__coursenumber',)

    def queryset(self, request):
        qs = Exam.all.get_query_set()
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Exam, ExamAdmin)

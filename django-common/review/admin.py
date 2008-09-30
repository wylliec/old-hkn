from django.contrib import admin
from review.models import Problem


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('name', 'tags', 'submitted')




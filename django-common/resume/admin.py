from django.contrib import admin
from resume.models import Resume

class ResumeAdmin(admin.ModelAdmin):
    list_display = (lambda resume: resume.person.name, 'overall_gpa', 'submitted')
    
admin.site.register(Resume, ResumeAdmin)
    

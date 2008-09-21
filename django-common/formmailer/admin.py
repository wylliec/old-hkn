from django.contrib import admin
from formmailer.models import MailTarget, MailMessage

class MailTargetAdmin(admin.ModelAdmin):
    pass

class MailMessageAdmin(admin.ModelAdmin):
    pass

admin.site.register(MailTarget, MailTargetAdmin)
admin.site.register(MailMessage, MailMessageAdmin)

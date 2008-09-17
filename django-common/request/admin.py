from django.contrib import admin

from request.models import Request


class RequestAdmin(admin.ModelAdmin):
    list_display = ("content_type", "title", "description")

admin.site.register(Request, RequestAdmin)

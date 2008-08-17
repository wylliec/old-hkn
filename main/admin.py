from django.contrib.admin.sites import AdminSite
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from photologue.admin import GalleryAdmin, PhotoAdmin, PhotoEffectAdmin, PhotoSizeAdmin, WatermarkAdmin
from photologue.models import Gallery, GalleryUpload, PhotoEffect, PhotoSize, Watermark, Photo

admin_site = AdminSite()
admin_site.register(FlatPage, FlatPageAdmin)

admin_site.register(Gallery, GalleryAdmin)
admin_site.register(GalleryUpload)
admin_site.register(Photo, PhotoAdmin)
admin_site.register(PhotoEffect, PhotoEffectAdmin)
admin_site.register(PhotoSize, PhotoSizeAdmin)
admin_site.register(Watermark, WatermarkAdmin)


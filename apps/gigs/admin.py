from django.contrib import admin
from apps.gigs.models import *

admin.site.register(Gig, admin.ModelAdmin)
admin.site.register(Category, admin.ModelAdmin)
admin.site.register(UserImage, admin.ModelAdmin)
admin.site.register(Feature, admin.ModelAdmin)
admin.site.register(Package, admin.ModelAdmin)
admin.site.register(Extra, admin.ModelAdmin)
admin.site.register(Requirement, admin.ModelAdmin)
admin.site.register(RequirementClient, admin.ModelAdmin)
admin.site.register(Review, admin.ModelAdmin)
admin.site.register(Order, admin.ModelAdmin)
admin.site.register(UserFile, admin.ModelAdmin)

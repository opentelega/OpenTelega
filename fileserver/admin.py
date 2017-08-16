from django.contrib import admin

from fileserver.models import User, File, Option

admin.site.register(User)
admin.site.register(File)
admin.site.register(Option)
# Register your models here.

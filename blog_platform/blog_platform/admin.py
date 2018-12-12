from django.contrib import admin
from blog_platform import models

admin.site.register(models.Post)
admin.site.register(models.Comment)

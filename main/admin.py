from django.contrib import admin

# Register your models here.
from main.models import SiteSettings

admin.site.register(SiteSettings)

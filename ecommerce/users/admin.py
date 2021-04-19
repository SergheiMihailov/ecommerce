from django.contrib import admin
from . models import Profile


class SearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'email']
    search_fields = ['user']
    list_filter = ['email']


admin.site.register(Profile)

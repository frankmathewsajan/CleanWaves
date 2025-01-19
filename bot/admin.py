from django.contrib import admin

from .models import Profile, Garbage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")


admin.site.register(Garbage)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Status", {"fields": ("is_online", "last_seen")}),
    )
    list_display = ("username", "email", "is_online", "last_seen", "is_staff")
    list_filter = ("is_online", "is_staff", "is_superuser")
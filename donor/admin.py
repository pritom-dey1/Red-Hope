from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import ContactMessage, Profile

# ContactMessage register
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")

# Profile register
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "blood_group", "role")

# User admin customize করে Profile inline করা
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
from django.contrib import admin
from .models import Hero

admin.site.register(Hero)

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import RequestPost, DonationRequest, Comment, Profile, ContactMessage, Hero


# =====================
# RequestPost Admin
# =====================
@admin.register(RequestPost)
class RequestPostAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "blood_group", "location", "post_type", "user", "created_at")
    search_fields = ("name", "problem", "blood_group", "location", "user__username")
    list_filter = ("blood_group", "location", "post_type", "created_at")
    ordering = ("-created_at",)


# =====================
# DonationRequest Admin
# =====================
@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "status", "post", "donor", "created_at")
    search_fields = ("name", "email", "phone", "post__name", "donor__username")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)


# =====================
# Comment Admin
# =====================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username", "post__name", "text")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


# =====================
# Profile Admin
# =====================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "blood_group", "role")
    list_filter = ("blood_group", "role")


# =====================
# ContactMessage Admin
# =====================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


# =====================
# Hero Admin
# =====================
@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "title")
    search_fields = ("name", "title", "description")


# =====================
# Custom User + Profile inline
# =====================
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

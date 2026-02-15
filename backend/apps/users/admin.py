from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import StudentProfile, StudentTeacherLink, TeacherProfile, User


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = "Student Profile"
    fk_name = "user"


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = "Teacher Profile"
    fk_name = "user"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "user_type", "is_active", "created_at")
    list_filter = ("user_type", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)

    # Override fieldsets since we removed username
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "user_type")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "user_type", "password1", "password2"),
            },
        ),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.user_type == "student":
            return [StudentProfileInline]
        if obj.user_type == "teacher":
            return [TeacherProfileInline]
        return []


@admin.register(StudentTeacherLink)
class StudentTeacherLinkAdmin(admin.ModelAdmin):
    list_display = ("student", "teacher", "linked_at")
    list_filter = ("linked_at",)

"""
User models for MathEd Romania.

Architecture: Single User model with a `user_type` field, plus separate
profile models (StudentProfile, TeacherProfile) for type-specific data.
This avoids multi-table inheritance headaches while keeping auth simple.

IMPORTANT: AUTH_USER_MODEL = "users.User" is set in base settings.
This file MUST exist before running the first migration.
"""
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .managers import UserManager

from decimal import Decimal


class User(AbstractUser):
    """
    Custom user model. Email-based authentication instead of username.
    """

    class UserType(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        ADMIN = "admin", "Admin"

    # Remove username field — we use email for auth
    username = None
    email = models.EmailField("email address", unique=True)

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.STUDENT,
    )

    # Shared fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_student(self):
        return self.user_type == self.UserType.STUDENT

    @property
    def is_teacher(self):
        return self.user_type == self.UserType.TEACHER


class StudentProfile(models.Model):
    """
    Student-specific data. Created automatically when a student registers.
    """

    class ConsentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    grade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(8)],
        help_text="Grade level (5-8)",
    )
    birth_date = models.DateField()
    parent_email = models.EmailField(
        blank=True,
        help_text="Required for students under 16 (GDPR)",
    )
    consent_status = models.CharField(
        max_length=10,
        choices=ConsentStatus.choices,
        default=ConsentStatus.PENDING,
    )
    consent_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "student_profiles"

    def __str__(self):
        return f"Student: {self.user.get_full_name()} (Grade {self.grade})"


class TeacherProfile(models.Model):
    """
    Teacher-specific data. Created automatically when a teacher registers.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    referral_code = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
    )
    commission_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.25,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
        help_text="Commission rate (0.20 = 20%)",
    )
    school_name = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "teacher_profiles"

    def __str__(self):
        return f"Teacher: {self.user.get_full_name()} ({self.referral_code})"


class StudentTeacherLink(models.Model):
    """
    Links students to their teacher. A student can have one active teacher link.
    """

    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_link",
        limit_choices_to={"user_type": "student"},
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_links",
        limit_choices_to={"user_type": "teacher"},
    )
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_teacher_links"

    def __str__(self):
        return f"{self.student.email} → {self.teacher.email}"

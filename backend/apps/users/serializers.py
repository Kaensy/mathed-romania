"""
Serializers for user registration, authentication, and profiles.

Registration flow:
- Student: requires grade, birth_date, parent_email (if under 16).
  Account is created but inactive until parental consent is given (if needed).
- Teacher: requires school_name (optional). Account activates immediately.
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import StudentProfile, TeacherProfile

User = get_user_model()

CONSENT_AGE = 16  # GDPR: under 16 requires parental consent


class StudentRegistrationSerializer(serializers.Serializer):
    """Handles student registration with age-based consent logic."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    grade = serializers.IntegerField(min_value=5, max_value=8)
    birth_date = serializers.DateField()
    parent_email = serializers.EmailField(required=False, allow_blank=True)

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        # Calculate age
        today = date.today()
        birth = data["birth_date"]
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

        # Under 16: parent_email is required
        if age < CONSENT_AGE:
            parent_email = data.get("parent_email", "").strip()
            if not parent_email:
                raise serializers.ValidationError(
                    {"parent_email": "Parent email is required for students under 16."}
                )
            if parent_email.lower() == data["email"].lower():
                raise serializers.ValidationError(
                    {"parent_email": "Parent email must be different from student email."}
                )

        data["_age"] = age
        return data

    def create(self, validated_data):
        age = validated_data.pop("_age")
        validated_data.pop("password_confirm")
        needs_consent = age < CONSENT_AGE

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            user_type=User.UserType.STUDENT,
            is_active=not needs_consent,  # Inactive until parent consents
        )

        StudentProfile.objects.create(
            user=user,
            grade=validated_data["grade"],
            birth_date=validated_data["birth_date"],
            parent_email=validated_data.get("parent_email", ""),
            consent_status=(
                StudentProfile.ConsentStatus.PENDING
                if needs_consent
                else StudentProfile.ConsentStatus.APPROVED
            ),
        )

        return user


class TeacherRegistrationSerializer(serializers.Serializer):
    """Handles teacher registration. Accounts activate immediately."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    school_name = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        school_name = validated_data.pop("school_name", "")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            user_type=User.UserType.TEACHER,
            is_active=True,
        )

        TeacherProfile.objects.create(
            user=user,
            school_name=school_name,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Returns user info + type-specific profile data."""

    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "user_type", "profile", "created_at"]
        read_only_fields = fields

    def get_profile(self, obj):
        if obj.is_student and hasattr(obj, "student_profile"):
            return StudentProfileSerializer(obj.student_profile).data
        if obj.is_teacher and hasattr(obj, "teacher_profile"):
            return TeacherProfileSerializer(obj.teacher_profile).data
        return None


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ["grade", "birth_date", "consent_status"]


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ["referral_code", "school_name", "commission_rate"]


class PasswordResetRequestSerializer(serializers.Serializer):
    """Step 1: User provides email to receive reset link."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Step 2: User provides new password with token from email."""

    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return data

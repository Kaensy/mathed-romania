"""
Authentication views for MathEd Romania.

JWT tokens are stored in httpOnly cookies (not localStorage) for security,
since our primary users are minors. The frontend never sees the raw tokens.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import StudentProfile
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    StudentRegistrationSerializer,
    TeacherRegistrationSerializer,
    UserProfileSerializer,
)

User = get_user_model()


# =============================================================================
# Cookie helpers
# =============================================================================

def _set_auth_cookies(response, user):
    """Generate JWT tokens and set them as httpOnly cookies."""
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    # Include user_type in token claims for frontend convenience
    refresh["user_type"] = user.user_type

    is_secure = getattr(settings, "SIMPLE_JWT", {}).get("AUTH_COOKIE_SECURE", True)

    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        secure=is_secure,
        samesite="Lax",
        max_age=60 * 30,  # 30 minutes
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=is_secure,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/api/v1/auth/token/refresh/",  # Only sent to refresh endpoint
    )
    return response


def _clear_auth_cookies(response):
    """Remove JWT cookies on logout."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth/token/refresh/")
    return response


# =============================================================================
# Registration
# =============================================================================

class StudentRegistrationView(APIView):
    """
    POST /api/v1/auth/register/student/

    Creates student account. If under 16, account is inactive
    and parental consent email is sent.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = StudentRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if not user.is_active:
            # Under 16 — send consent email
            self._send_consent_email(user)
            return Response(
                {
                    "message": "Account created. A consent email has been sent to your parent. "
                    "Your account will be activated once they approve.",
                    "requires_consent": True,
                },
                status=status.HTTP_201_CREATED,
            )

        # 16+ — account is active, log them in immediately
        response = Response(
            {
                "message": "Account created successfully.",
                "requires_consent": False,
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
        return _set_auth_cookies(response, user)

    def _send_consent_email(self, user):
        """Send parental consent email with approval link."""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        profile = user.student_profile

        # TODO: Replace with actual frontend URL in production
        consent_link = (
            f"{settings.FRONTEND_URL}/consent/approve?uid={uid}&token={token}"
        )

        # In development, this prints to console (EMAIL_BACKEND = console)
        from django.core.mail import send_mail

        send_mail(
            subject="MathEd Romania — Consimțământ parental necesar",
            message=(
                f"Bună ziua,\n\n"
                f"{user.get_full_name()} dorește să-și creeze un cont pe MathEd Romania.\n\n"
                f"Pentru a aproba crearea contului, accesați link-ul următor:\n"
                f"{consent_link}\n\n"
                f"Dacă nu ați solicitat acest lucru, ignorați acest email.\n\n"
                f"Echipa MathEd Romania"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.parent_email],
            fail_silently=False,
        )


class TeacherRegistrationView(APIView):
    """
    POST /api/v1/auth/register/teacher/

    Creates teacher account. Activates immediately.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TeacherRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = Response(
            {
                "message": "Account created successfully.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
        return _set_auth_cookies(response, user)


# =============================================================================
# Parental Consent
# =============================================================================

class ParentalConsentView(APIView):
    """
    POST /api/v1/auth/consent/approve/

    Parent clicks the link in email, frontend calls this endpoint
    to activate the student account.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")

        if not uid or not token:
            return Response(
                {"error": "Missing uid or token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid consent link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Consent link has expired or is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active:
            return Response(
                {"message": "Account is already active."},
                status=status.HTTP_200_OK,
            )

        # Activate the account
        user.is_active = True
        user.save(update_fields=["is_active"])

        # Update consent status
        from django.utils import timezone

        StudentProfile.objects.filter(user=user).update(
            consent_status=StudentProfile.ConsentStatus.APPROVED,
            consent_date=timezone.now(),
        )

        return Response(
            {"message": "Consent approved. The student can now log in."},
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Login / Logout / Token Refresh
# =============================================================================

class LoginView(APIView):
    """
    POST /api/v1/auth/login/

    Email + password login. Sets JWT cookies on success.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            # Check if it's a pending consent issue
            if (
                user.is_student
                and hasattr(user, "student_profile")
                and user.student_profile.consent_status == StudentProfile.ConsentStatus.PENDING
            ):
                return Response(
                    {"error": "Your account is awaiting parental consent. "
                     "Please ask your parent to check their email."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                {"error": "Your account is inactive. Please contact support."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = Response(
            {
                "message": "Login successful.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
        return _set_auth_cookies(response, user)


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/

    Blacklists the refresh token and clears cookies.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response = Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )

        # Try to blacklist the refresh token
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # Token may already be blacklisted or invalid

        return _clear_auth_cookies(response)


class CookieTokenRefreshView(APIView):
    """
    POST /api/v1/auth/token/refresh/

    Reads refresh token from httpOnly cookie, returns new access token
    also as a cookie. The frontend never handles raw tokens.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "No refresh token found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            user = User.objects.get(id=refresh["user_id"])
        except Exception:
            response = Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            return _clear_auth_cookies(response)

        # Rotate the refresh token
        refresh.blacklist()

        response = Response(
            {"message": "Token refreshed."},
            status=status.HTTP_200_OK,
        )
        return _set_auth_cookies(response, user)


# =============================================================================
# User Profile
# =============================================================================

class UserProfileView(APIView):
    """
    GET /api/v1/auth/me/

    Returns the authenticated user's profile info.
    Used by frontend to check auth state on page load.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserProfileSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Password Reset
# =============================================================================

class PasswordResetRequestView(APIView):
    """
    POST /api/v1/auth/password-reset/

    Sends password reset email. Always returns 200 to prevent
    email enumeration.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()

        try:
            user = User.objects.get(email=email, is_active=True)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

            from django.core.mail import send_mail

            send_mail(
                subject="MathEd Romania — Resetare parolă",
                message=(
                    f"Bună,\n\n"
                    f"Am primit o cerere de resetare a parolei pentru contul tău.\n\n"
                    f"Accesează link-ul următor pentru a seta o parolă nouă:\n"
                    f"{reset_link}\n\n"
                    f"Dacă nu ai solicitat acest lucru, ignoră acest email.\n\n"
                    f"Echipa MathEd Romania"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists

        return Response(
            {"message": "If an account with that email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    POST /api/v1/auth/password-reset/confirm/

    Validates token and sets new password.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return Response(
                {"error": "Reset link has expired or is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"message": "Password reset successful. You can now log in."},
            status=status.HTTP_200_OK,
        )

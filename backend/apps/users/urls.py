from django.urls import path

from .views import (
    CookieTokenRefreshView,
    LoginView,
    LogoutView,
    ParentalConsentView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    StudentRegistrationView,
    TeacherRegistrationView,
    UserProfileView,
)

urlpatterns = [
    # Registration
    path("register/student/", StudentRegistrationView.as_view(), name="register_student"),
    path("register/teacher/", TeacherRegistrationView.as_view(), name="register_teacher"),

    # Parental consent
    path("consent/approve/", ParentalConsentView.as_view(), name="consent_approve"),

    # Login / Logout / Refresh
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),

    # Profile
    path("me/", UserProfileView.as_view(), name="user_profile"),

    # Password reset
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]

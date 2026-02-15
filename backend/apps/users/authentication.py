"""
Custom JWT authentication backend that reads tokens from httpOnly cookies
instead of the Authorization header.

This is critical for security since our users are minors — tokens
should never be accessible to JavaScript (prevents XSS token theft).
"""
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Extends SimpleJWT to read the access token from an httpOnly cookie.
    Falls back to the Authorization header for API testing tools like Postman.
    """

    def authenticate(self, request):
        # First try the cookie
        raw_token = request.COOKIES.get("access_token")

        if raw_token is not None:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token

        # Fall back to Authorization header (useful for testing)
        return super().authenticate(request)

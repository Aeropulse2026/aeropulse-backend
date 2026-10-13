from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class BearerTokenAuthentication(TokenAuthentication):
    """Use DRF token records with the standard HTTP Bearer scheme."""
    keyword = "Bearer"


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate an API request from a Bearer header or HttpOnly access cookie."""
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)
        raw_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

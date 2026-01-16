import datetime
import logging
import secrets
import jwt
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class UserAuthenticationSystem:
    """
    SQL Based JWT Authentication System
    """

    def __init__(self):
        self.jwt_secret = settings.SECRET_KEY

    # ------------------------------------------------
    # ACCESS TOKEN
    # ------------------------------------------------
    def generate_access_token(self, email, refresh_token, session_id=None):
        try:
            user = User.objects.get(email=email)

            if not user.is_refresh_token_valid(refresh_token):
                return {
                    "is_successful": False,
                    "message": "Refresh token invalid or expired",
                }

            payload = {
                      "email": user.email,
                      "user_type": user.user_type,
                      "session_id": session_id,
                      "iat": timezone.now(),
                      "exp": timezone.now() + timedelta(minutes=30),
                     }


            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")

            return {
                "is_successful": True,
                "access_token": token,
                "expires_in": 1800,
            }

        except User.DoesNotExist:
            return {"is_successful": False, "message": "User not found"}

        except Exception as e:
            logger.error(e)
            return {"is_successful": False, "message": str(e)}

    # ------------------------------------------------
    # JWT VALIDATION
    # ------------------------------------------------
    def validate_access_token(self, token):
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return {"is_valid": True, "payload": payload}

        except jwt.ExpiredSignatureError:
            return {"is_valid": False, "message": "Token expired"}

        except jwt.InvalidTokenError:
            return {"is_valid": False, "message": "Invalid token"}

    # ------------------------------------------------
    # REFRESH TOKEN
    # ------------------------------------------------
    @staticmethod
    def generate_refresh_token():
        return secrets.token_urlsafe(40)

    def issue_refresh_token(self, user):
        token = self.generate_refresh_token()
        user.set_refresh_token(token, days=1)
        return token

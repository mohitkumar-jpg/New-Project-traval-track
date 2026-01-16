from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage


class SuperAdminLoginAPI(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            return Response(
                {"success": False, "message": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "success": True,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
            }
        })


class SuperAdminLogoutAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({"success": True})



class SuperAdminForgotPasswordAPI(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email, is_superuser=True).first()

        if not user:
            return Response({"message": "Super admin not found"}, status=404)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = f"http://localhost:3000/super-admin/reset-password/{uid}/{token}"

        EmailMessage(
            subject="Super Admin Password Reset",
            body=f"Reset password link:\n{reset_link}",
            to=[email],
        ).send()

        return Response({"success": True, "message": "Reset link sent"})


class SuperAdminResetPasswordAPI(APIView):
    permission_classes = []

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        password = request.data.get("password")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_superuser=True)
        except:
            return Response({"message": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"message": "Token expired"}, status=400)

        user.set_password(password)
        user.save()

        return Response({"success": True})


class SuperAdminProfileAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "role": "super_admin"
        })

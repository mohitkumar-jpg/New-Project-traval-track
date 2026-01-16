from django.urls import path
from dashboards.users.api.login import LoginAPI
from dashboards.users.api.logout import LogoutAPI
from django.contrib.auth import get_user_model
User = get_user_model()




urlpatterns = [
    path("login/", LoginAPI.as_view(), name="super_admin_login"),
    path("logout/", LogoutAPI.as_view()),
   
]
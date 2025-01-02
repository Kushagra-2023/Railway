from django.urls import path
from .views import *

urlpatterns = [
    path("register", RegistrationView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("passwordchange", PasswordChangeView.as_view(), name="passwordchange"),
    path("usernamechange", UsernameChangeView.as_view(), name="usernamechange"),
    path("getinfo", GetInfo.as_view(), name="getinfo")
]
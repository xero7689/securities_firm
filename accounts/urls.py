from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.account_form, name="account_form"),
    path("status/", views.account_status, name="account_status"),
    path("congratulations/", views.congratulations, name="congratulations"),
]

from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html", next_page="account_status"
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("", views.home, name="home"),
    path("supplement/", views.supplement_form, name="supplement_form"),
    path("status/", views.account_status, name="account_status"),
    path(
        "admin-without-account/",
        views.admin_without_account,
        name="admin_without_account",
    ),
    path("congratulations/", views.congratulations, name="congratulations"),
]

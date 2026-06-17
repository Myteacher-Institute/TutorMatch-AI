from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify/", views.verify_account, name="verify_account"),
    path("password-reset/", views.password_reset, name="password_reset"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
]

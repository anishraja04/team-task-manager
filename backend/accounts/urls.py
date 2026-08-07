from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("me/", views.MeView.as_view(), name="me"),
    path("users/", views.UserSearchView.as_view(), name="user-search"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

from django.urls import path, include
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserLibraryAccountProfileView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", UserLibraryAccountProfileView.as_view(), name="profile"),
]

from django.urls import path

from .views import (
    WebLoginView,
    edit_profile,
    logout_confirm,
    mark_notifications_read,
    notifications_api,
    profile,
    register,
)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", WebLoginView.as_view(), name="login"),
    path("logout/", logout_confirm, name="logout"),
    path("profile/", profile, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("notifications/read/", mark_notifications_read, name="mark_notifications_read"),
    path("notifications/", notifications_api, name="notifications_api"),
]


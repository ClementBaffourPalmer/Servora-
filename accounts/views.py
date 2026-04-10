from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import RegistrationForm
from .models import Notification, ProviderProfile, User


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            if user.is_provider:
                ProviderProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Welcome to Servora!")
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


class WebLoginView(LoginView):
    template_name = "accounts/login.html"


@login_required
def logout_confirm(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You’ve been logged out.")
        return redirect("home")
    return render(request, "accounts/logout.html", {"next": request.GET.get("next") or reverse_lazy("home")})


@login_required
def profile(request):
    provider_profile = getattr(request.user, "provider_profile", None)
    notifications = request.user.notifications.all()[:8]
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(
        request,
        "accounts/profile.html",
        {"provider_profile": provider_profile, "notifications": notifications, "unread_count": unread_count},
    )


@login_required
def edit_profile(request):
    from .forms import EditProfileForm, ProviderProfileForm  # noqa: WPS433

    user_form = EditProfileForm(instance=request.user, data=request.POST or None, files=request.FILES or None)
    profile_form = None
    if request.user.is_provider:
        provider_profile, _ = ProviderProfile.objects.get_or_create(user=request.user)
        profile_form = ProviderProfileForm(instance=provider_profile, data=request.POST or None)

    if request.method == "POST":
        valid = user_form.is_valid()
        if profile_form is not None:
            valid = valid and profile_form.is_valid()
        if valid:
            user_form.save()
            if profile_form is not None:
                profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")

    return render(
        request,
        "accounts/edit_profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.GET.get("next") or "profile")


@login_required
def notifications_api(request):
    unread = Notification.objects.filter(user=request.user, is_read=False).order_by("-created_at")
    payload = [
        {
            "id": item.id,
            "title": item.title,
            "message": item.message,
            "link": item.link,
            "created_at": item.created_at.isoformat(),
        }
        for item in unread[:20]
    ]
    return JsonResponse({"unread_count": unread.count(), "items": payload})


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Notification, ProviderProfile, ProviderSubscription, SubscriptionPlan, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Servora", {"fields": ("role", "avatar")}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "phone", "whatsapp_number", "available_from", "available_to")
    search_fields = ("user__username", "display_name", "phone", "whatsapp_number")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title", "message")


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "max_services", "max_bookings_per_day")
    search_fields = ("name",)


@admin.register(ProviderSubscription)
class ProviderSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("provider", "plan", "start_date", "active")
    list_filter = ("active", "plan", "start_date")
    search_fields = ("provider__username", "plan__name")


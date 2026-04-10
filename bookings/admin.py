from django.contrib import admin

from .models import Booking, ServicePayment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("service", "customer", "date", "time", "status", "created_at")
    list_filter = ("status", "date")
    search_fields = ("service__name", "customer__username", "contact_name", "contact_phone")


@admin.register(ServicePayment)
class ServicePaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "service", "customer", "provider", "amount", "network", "status", "created_at")
    list_filter = ("status", "network", "created_at")
    search_fields = ("reference", "service__name", "customer__username", "provider__username", "phone")


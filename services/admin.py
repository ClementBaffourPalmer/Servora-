from django.contrib import admin

from .models import AvailabilitySlot, Review, Service, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


class AvailabilitySlotInline(admin.TabularInline):
    model = AvailabilitySlot
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "provider", "price", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "provider__username")
    inlines = [AvailabilitySlotInline]


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ("service", "date", "time", "is_active")
    list_filter = ("is_active", "date")
    search_fields = ("service__name", "service__provider__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("service", "customer", "rating", "created")
    list_filter = ("rating", "created")
    search_fields = ("service__name", "customer__username", "comment")


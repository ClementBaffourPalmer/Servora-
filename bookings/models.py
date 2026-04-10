from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from services.models import AvailabilitySlot, Service


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_bookings",
        null=True,
        blank=True,
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="bookings")
    slot = models.ForeignKey(
        AvailabilitySlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    contact_name = models.CharField(max_length=120)
    contact_phone = models.CharField(max_length=50)
    contact_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["service", "date", "time"],
                condition=~Q(status="cancelled"),
                name="uniq_non_cancelled_booking_per_service_slot",
            )
        ]

    def __str__(self) -> str:
        return f"{self.customer} -> {self.service} ({self.date} {self.time})"

    @property
    def booking_date(self):
        return self.date

    @property
    def booking_time(self):
        return self.time


class ServicePayment(models.Model):
    class Network(models.TextChoices):
        MTN = "mtn", "MTN"
        TELECEL = "telecel", "Telecel"
        AT = "at", "AT"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_payments",
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_service_payments",
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=20)
    network = models.CharField(max_length=20, choices=Network.choices)
    reference = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.reference} - {self.service.name} ({self.status})"


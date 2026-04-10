from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        PROVIDER = "provider", "Service Provider"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    @property
    def is_provider(self) -> bool:
        return self.role == self.Role.PROVIDER

    @property
    def is_customer(self) -> bool:
        return self.role == self.Role.CUSTOMER


class ProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="provider_profile")
    display_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    snapchat = models.CharField(max_length=100, blank=True)
    tiktok = models.CharField(max_length=100, blank=True)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.display_name or self.user.get_username()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=140)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.title}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_services = models.IntegerField(default=3)
    max_bookings_per_day = models.IntegerField(default=5)

    class Meta:
        ordering = ["price", "name"]

    def __str__(self) -> str:
        return self.name

    @property
    def max_services_label(self) -> str:
        return "Unlimited" if self.max_services < 0 else str(self.max_services)

    @property
    def max_bookings_per_day_label(self) -> str:
        return "Unlimited" if self.max_bookings_per_day < 0 else str(self.max_bookings_per_day)


class ProviderSubscription(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="subscriptions")
    start_date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.provider.username} - {self.plan.name}"


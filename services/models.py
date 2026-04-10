from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ServiceCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Service categories"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="services",
    )
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="services")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.provider})"


class AvailabilitySlot(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="availability_slots")
    date = models.DateField()
    time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("service", "date", "time")
        ordering = ["date", "time"]

    def __str__(self) -> str:
        return f"{self.service.name} — {self.date} {self.time}"


class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_reviews")
    rating = models.IntegerField()
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.service.name} review by {self.customer}"


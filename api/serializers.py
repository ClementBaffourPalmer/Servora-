from django.contrib.auth import authenticate
from rest_framework import serializers

from accounts.models import ProviderProfile, User
from bookings.models import Booking
from services.models import AvailabilitySlot, Service, ServiceCategory


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if user.is_provider:
            ProviderProfile.objects.get_or_create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User is inactive.")
        attrs["user"] = user
        return attrs


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name")


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = ("id", "date", "time", "is_active")


class ServiceListSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer()
    provider_username = serializers.CharField(source="provider.username")

    class Meta:
        model = Service
        fields = ("id", "name", "category", "price", "provider_username", "image", "image_url", "is_active")


class ServiceDetailSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer()
    provider_username = serializers.CharField(source="provider.username")
    availability_slots = AvailabilitySlotSerializer(many=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "category",
            "price",
            "provider_username",
            "image",
            "image_url",
            "is_active",
            "availability_slots",
        )


class ProviderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "category", "name", "description", "price", "image", "image_url", "is_active")


class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "service",
            "service_name",
            "slot",
            "date",
            "time",
            "status",
            "status_display",
            "contact_name",
            "contact_phone",
            "contact_email",
            "notes",
            "created_at",
        )
        read_only_fields = ("status", "created_at")

    def validate(self, attrs):
        service = attrs["service"]
        slot = attrs.get("slot")
        if slot:
            if slot.service_id != service.id:
                raise serializers.ValidationError({"slot": "Slot does not belong to selected service."})
            if not slot.is_active:
                raise serializers.ValidationError({"slot": "Slot is not available."})
        else:
            if not attrs.get("date"):
                raise serializers.ValidationError({"date": "Date is required."})
            if not attrs.get("time"):
                raise serializers.ValidationError({"time": "Time is required."})
        return attrs

    def create(self, validated_data):
        slot = validated_data.get("slot")
        if slot:
            validated_data["date"] = slot.date
            validated_data["time"] = slot.time
        booking = Booking.objects.create(**validated_data)
        if slot:
            AvailabilitySlot.objects.filter(pk=slot.pk, is_active=True).update(is_active=False)
        return booking


class ProviderBookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("status",)

    def validate_status(self, value):
        allowed = {Booking.Status.CONFIRMED, Booking.Status.CANCELLED, Booking.Status.COMPLETED}
        if value not in allowed:
            raise serializers.ValidationError("Invalid status transition.")
        return value


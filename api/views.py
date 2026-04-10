from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.utils import create_notification
from bookings.models import Booking
from services.models import AvailabilitySlot, Service

from .permissions import IsAuthenticatedCustomer, IsAuthenticatedProvider
from .serializers import (
    BookingSerializer,
    LoginSerializer,
    ProviderBookingStatusSerializer,
    ProviderServiceSerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
    UserRegistrationSerializer,
)

BEAUTY_CATEGORIES = ["Nail Technician", "Wig & Frontals", "Hair Salon", "Barbering"]


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(
        is_active=True, category__name__in=BEAUTY_CATEGORIES
    ).select_related("category", "provider")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ServiceDetailSerializer
        return ServiceListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs


class ProviderServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderServiceSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedProvider]

    def get_queryset(self):
        return Service.objects.filter(
            provider=self.request.user, category__name__in=BEAUTY_CATEGORIES
        ).select_related("category")

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class CustomerBookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedCustomer]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return (
            Booking.objects.filter(customer=self.request.user)
            .select_related("service", "slot", "service__category", "service__provider")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                booking = serializer.save(customer=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "That appointment time is already booked. Please choose another time."}
            )

        send_mail(
            subject="Servora: Booking created",
            message=(
                f"Your booking for '{booking.service.name}' is created and pending.\n\n"
                f"Date: {booking.date}\nTime: {booking.time}\nStatus: {booking.get_status_display()}"
            ),
            from_email=None,
            recipient_list=[self.request.user.email] if self.request.user.email else [],
            fail_silently=True,
        )
        create_notification(
            user=self.request.user,
            title="Booking created",
            message=f"Your booking for {booking.service.name} is pending confirmation.",
            link="/bookings/me/",
        )
        create_notification(
            user=booking.service.provider,
            title="New booking request",
            message=f"{self.request.user.username} booked {booking.service.name}.",
            link="/provider/bookings/",
        )


class ProviderBookingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsAuthenticatedProvider]
    queryset = Booking.objects.select_related("service", "customer", "slot", "service__category")
    serializer_class = BookingSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return super().get_queryset().filter(service__provider=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["patch"], url_path="status")
    def status_update(self, request, pk=None):
        booking = self.get_object()
        serializer = ProviderBookingStatusSerializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data.get("status")
        booking.status = new_status
        booking.save(update_fields=["status", "updated_at"])
        if new_status == Booking.Status.CANCELLED and booking.slot_id:
            AvailabilitySlot.objects.filter(pk=booking.slot_id).update(is_active=True)
        create_notification(
            user=booking.customer,
            title="Booking status updated",
            message=f"{booking.service.name} is now {booking.get_status_display()}.",
            link="/bookings/me/",
        )
        return Response(BookingSerializer(booking).data)


from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, CustomerBookingViewSet, ProviderBookingViewSet, ProviderServiceViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"services", ServiceViewSet, basename="services")
router.register(r"provider/services", ProviderServiceViewSet, basename="provider-services")
router.register(r"bookings", CustomerBookingViewSet, basename="customer-bookings")
router.register(r"provider/bookings", ProviderBookingViewSet, basename="provider-bookings")

urlpatterns = [
    path("", include(router.urls)),
]


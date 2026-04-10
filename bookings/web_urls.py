from django.urls import path

from .views import (
    accept_booking,
    cancel_booking,
    create_booking,
    customer_booking_detail,
    customer_bookings,
    customer_dashboard,
    provider_update_booking_status,
    reject_booking,
)

urlpatterns = [
    path("new/<int:service_id>/", create_booking, name="create_booking"),
    path("me/", customer_dashboard, name="customer_dashboard"),
    path("", customer_bookings, name="customer_bookings"),
    path("<int:booking_id>/", customer_booking_detail, name="customer_booking_detail"),
    path("cancel/<int:booking_id>/", cancel_booking, name="cancel_booking"),
    path("accept/<int:booking_id>/", accept_booking, name="accept_booking"),
    path("reject/<int:booking_id>/", reject_booking, name="reject_booking"),
    path(
        "provider/<int:booking_id>/status/<str:status>/",
        provider_update_booking_status,
        name="provider_update_booking_status",
    ),
]


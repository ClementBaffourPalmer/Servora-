from django.urls import path

from .views import (
    HomeView,
    ProviderServiceCreateView,
    ProviderServiceListView,
    ProviderServiceUpdateView,
    admin_dashboard,
    provider_booking_detail,
    provider_bookings,
    provider_dashboard,
    provider_service_availability,
    provider_service_delete,
    pay_service_mobile_money,
    service_detail,
    submit_review,
    subscribe,
    subscription_plans,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("services/", HomeView.as_view(template_name="services/service_list.html"), name="service_list"),
    path("services/<int:pk>/", service_detail, name="service_detail"),
    path("services/<int:service_id>/reviews/", submit_review, name="submit_review"),
    path("services/<int:service_id>/pay/", pay_service_mobile_money, name="pay_service_mobile_money"),
    # Provider dashboard
    path("provider/", provider_dashboard, name="provider_dashboard"),
    path("provider/services/", ProviderServiceListView.as_view(), name="provider_services"),
    path("provider/services/new/", ProviderServiceCreateView.as_view(), name="provider_service_create"),
    path("provider/services/<int:pk>/edit/", ProviderServiceUpdateView.as_view(), name="provider_service_update"),
    path("provider/services/<int:pk>/delete/", provider_service_delete, name="provider_service_delete"),
    path(
        "provider/services/<int:service_id>/availability/",
        provider_service_availability,
        name="provider_service_availability",
    ),
    path("provider/bookings/", provider_bookings, name="provider_bookings"),
    path("provider/bookings/<int:booking_id>/", provider_booking_detail, name="provider_booking_detail"),
    path("provider/subscriptions/", subscription_plans, name="subscription_plans"),
    path("provider/subscriptions/<int:plan_id>/subscribe/", subscribe, name="subscribe"),
    path("platform/admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]


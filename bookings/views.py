from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.utils import create_notification
from services.models import Service

from .forms import BookingCreateForm
from .models import Booking, ServicePayment


@login_required
def create_booking(request, service_id: int):
    service = get_object_or_404(Service.objects.select_related("provider", "category"), pk=service_id, is_active=True)
    if request.user.is_provider:
        raise Http404()

    if request.method == "POST":
        form = BookingCreateForm(request.POST, service=service)
        if form.is_valid():
            try:
                with transaction.atomic():
                    booking = Booking.objects.create(
                        customer=request.user,
                        provider=service.provider,
                        service=service,
                        date=form.cleaned_data["date"],
                        time=form.cleaned_data["time"],
                        contact_name=form.cleaned_data["contact_name"],
                        contact_phone=form.cleaned_data["contact_phone"],
                        contact_email=form.cleaned_data["contact_email"],
                        notes=form.cleaned_data["notes"],
                    )
            except IntegrityError:
                messages.error(request, "That appointment time is already booked. Please choose another time.")
                return redirect("service_detail", pk=service.pk)

            send_mail(
                subject="Servora: Booking created",
                message=(
                    f"Your booking for '{service.name}' is created and pending.\n\n"
                    f"Date: {booking.date}\nTime: {booking.time}\nStatus: {booking.get_status_display()}"
                ),
                from_email=None,
                recipient_list=[request.user.email] if request.user.email else [],
                fail_silently=True,
            )
            create_notification(
                user=request.user,
                title="Booking created",
                message=f"Your booking for {service.name} is pending confirmation.",
                link="/bookings/me/",
            )
            create_notification(
                user=service.provider,
                title="New booking request",
                message=f"{request.user.username} booked {service.name} on {booking.date} at {booking.time}.",
                link="/provider/bookings/",
            )
            messages.success(request, "Booking created! The provider will confirm or reject it.")
            return redirect("customer_dashboard")
    else:
        form = BookingCreateForm(service=service)

    return render(request, "bookings/booking_form.html", {"service": service, "form": form})


@login_required
def customer_dashboard(request):
    if request.user.is_provider:
        raise Http404()
    bookings = (
        Booking.objects.filter(customer=request.user)
        .select_related("service", "service__provider", "service__category")
        .order_by("-created_at")
    )
    payments = (
        ServicePayment.objects.filter(customer=request.user, status=ServicePayment.Status.SUCCESS)
        .select_related("service", "provider")
        .order_by("-created_at")[:8]
    )
    total_spent = (
        ServicePayment.objects.filter(customer=request.user, status=ServicePayment.Status.SUCCESS).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )
    notifications = request.user.notifications.all()[:6]
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(
        request,
        "bookings/customer_dashboard.html",
        {
            "bookings": bookings,
            "payments": payments,
            "total_spent": total_spent,
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def customer_bookings(request):
    return customer_dashboard(request)


@login_required
def customer_booking_detail(request, booking_id: int):
    if request.user.is_provider:
        raise Http404()
    booking = get_object_or_404(
        Booking.objects.select_related("service", "service__provider", "service__category"),
        pk=booking_id,
        customer=request.user,
    )
    return render(request, "bookings/customer_booking_detail.html", {"booking": booking})


@login_required
def cancel_booking(request, booking_id: int):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)
    if booking.status == Booking.Status.CANCELLED:
        return redirect("customer_dashboard")
    booking.status = Booking.Status.CANCELLED
    booking.save(update_fields=["status", "updated_at"])
    create_notification(
        user=booking.service.provider,
        title="Booking cancelled",
        message=f"{request.user.username} cancelled booking for {booking.service.name}.",
        link="/provider/bookings/",
    )
    messages.success(request, "Booking cancelled.")
    return redirect("customer_dashboard")


@login_required
def provider_update_booking_status(request, booking_id: int, status: str):
    if not request.user.is_provider:
        raise Http404()
    booking = get_object_or_404(Booking.objects.select_related("service"), pk=booking_id, service__provider=request.user)
    allowed = {Booking.Status.CONFIRMED, Booking.Status.CANCELLED, Booking.Status.COMPLETED}
    if status not in allowed:
        raise Http404()

    booking.status = status
    booking.save(update_fields=["status", "updated_at"])
    status_label = {
        Booking.Status.CONFIRMED: "Accepted",
        Booking.Status.CANCELLED: "Rejected",
        Booking.Status.COMPLETED: "Completed",
    }.get(status, booking.get_status_display())
    create_notification(
        user=booking.customer,
        title="Booking status updated",
        message=f"{booking.service.name} is now {status_label}.",
        link="/bookings/me/",
    )
    messages.success(request, f"Booking updated to {status_label}.")
    return redirect("provider_bookings")


@login_required
def accept_booking(request, booking_id: int):
    return provider_update_booking_status(request, booking_id, Booking.Status.CONFIRMED)


@login_required
def reject_booking(request, booking_id: int):
    return provider_update_booking_status(request, booking_id, Booking.Status.CANCELLED)


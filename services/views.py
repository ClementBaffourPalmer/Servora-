from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Prefetch, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView
from uuid import uuid4

from bookings.models import Booking, ServicePayment
from accounts.models import Notification, ProviderSubscription, SubscriptionPlan, User
from accounts.utils import create_notification

from .forms import AvailabilitySlotForm, ServiceForm
from .models import AvailabilitySlot, Review, Service, ServiceCategory
from .utils import ensure_provider_has_starter_services

MARKETPLACE_CATEGORIES = ["Nail Technician", "Wig & Frontals", "Hair Salon", "Barbering", "Laundry", "Welding"]


class HomeView(ListView):
    template_name = "services/home.html"
    context_object_name = "services"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Service.objects.filter(is_active=True)
            .select_related("category", "provider")
            .order_by("-created_at")
        )
        qs = qs.filter(category__name__in=MARKETPLACE_CATEGORIES)
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category__id=category)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = ServiceCategory.objects.filter(name__in=MARKETPLACE_CATEGORIES).order_by("name")
        ctx["selected_category"] = self.request.GET.get("category", "")
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


def service_detail(request, pk: int):
    service = get_object_or_404(
        Service.objects.select_related("category", "provider").prefetch_related(
            Prefetch(
                "availability_slots",
                queryset=AvailabilitySlot.objects.filter(is_active=True).order_by("date", "time"),
            )
        ),
        pk=pk,
        is_active=True,
    )
    reviews = service.reviews.select_related("customer").all()
    avg_rating = reviews.aggregate(value=Avg("rating"))["value"]
    provider_profile = getattr(service.provider, "provider_profile", None)
    return render(
        request,
        "services/service_detail.html",
        {
            "service": service,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "provider_profile": provider_profile,
        },
    )


def _provider_active_subscription(user: User):
    return (
        ProviderSubscription.objects.select_related("plan")
        .filter(provider=user, active=True)
        .order_by("-start_date")
        .first()
    )


class ProviderRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return bool(self.request.user.is_authenticated and getattr(self.request.user, "is_provider", False))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise Http404()
        return super().handle_no_permission()


class ProviderServiceListView(LoginRequiredMixin, ProviderRequiredMixin, ListView):
    template_name = "services/provider_services.html"
    context_object_name = "services"

    def get_queryset(self):
        ensure_provider_has_starter_services(self.request.user)
        return Service.objects.filter(provider=self.request.user).select_related("category").order_by("-created_at")


@login_required
def provider_dashboard(request):
    if not request.user.is_provider:
        raise Http404()
    ensure_provider_has_starter_services(request.user)
    services_count = Service.objects.filter(provider=request.user).count()
    bookings_count = Booking.objects.filter(service__provider=request.user).count()
    pending_count = Booking.objects.filter(service__provider=request.user, status=Booking.Status.PENDING).count()
    today = timezone.localdate()
    bookings_today = (
        Booking.objects.filter(service__provider=request.user, date=today)
        .select_related("service", "customer", "service__category")
        .order_by("time")
    )
    count_today = bookings_today.count()
    services = (
        Service.objects.filter(provider=request.user, is_active=True)
        .select_related("category")
        .order_by("-created_at")[:4]
    )
    bookings = (
        Booking.objects.filter(service__provider=request.user)
        .select_related("service", "service__category")
        .order_by("-created_at")[:6]
    )
    provider_payments = (
        ServicePayment.objects.filter(provider=request.user, status=ServicePayment.Status.SUCCESS)
        .select_related("service", "customer")
        .order_by("-created_at")[:8]
    )
    total_earnings = (
        ServicePayment.objects.filter(provider=request.user, status=ServicePayment.Status.SUCCESS).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )
    notifications = Notification.objects.filter(user=request.user)[:6]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(
        request,
        "services/provider_dashboard.html",
        {
            "services_count": services_count,
            "bookings_count": bookings_count,
            "pending_count": pending_count,
            "bookings_today": bookings_today,
            "count_today": count_today,
            "provider_payments": provider_payments,
            "total_earnings": total_earnings,
            "services": services,
            "bookings": bookings,
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def provider_booking_detail(request, booking_id: int):
    if not request.user.is_provider:
        raise Http404()
    booking = get_object_or_404(
        Booking.objects.select_related("service", "customer", "service__category"),
        pk=booking_id,
        service__provider=request.user,
    )
    return render(request, "services/provider_booking_detail.html", {"booking": booking})


@login_required
def provider_service_delete(request, pk: int):
    if not request.user.is_provider:
        raise Http404()
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == "POST":
        service.delete()
        messages.success(request, "Service deleted.")
        return redirect("provider_services")
    return render(request, "services/provider_service_delete.html", {"service": service})


class ProviderServiceCreateView(LoginRequiredMixin, ProviderRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "services/provider_service_form.html"
    success_url = reverse_lazy("provider_services")

    def form_valid(self, form):
        subscription = _provider_active_subscription(self.request.user)
        if subscription and subscription.plan.max_services >= 0:
            service_count = Service.objects.filter(provider=self.request.user).count()
            if service_count >= subscription.plan.max_services:
                messages.error(self.request, "Upgrade plan to add more services.")
                return redirect("subscription_plans")
        form.instance.provider = self.request.user
        messages.success(self.request, "Service created.")
        return super().form_valid(form)


class ProviderServiceUpdateView(LoginRequiredMixin, ProviderRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "services/provider_service_form.html"

    def get_queryset(self):
        return Service.objects.filter(provider=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Service updated.")
        return reverse("provider_services")


@login_required
def provider_service_availability(request, service_id: int):
    service = get_object_or_404(Service, pk=service_id, provider=request.user)
    if request.method == "POST":
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.service = service
            slot.save()
            messages.success(request, "Availability slot added.")
            return redirect("provider_service_availability", service_id=service.id)
    else:
        form = AvailabilitySlotForm()

    slots = service.availability_slots.all().order_by("date", "time")
    return render(
        request,
        "services/provider_availability.html",
        {"service": service, "form": form, "slots": slots},
    )


@login_required
def provider_bookings(request):
    if not request.user.is_provider:
        raise Http404()
    qs = (
        Booking.objects.filter(service__provider=request.user)
        .select_related("service", "customer", "service__category")
        .order_by("-created_at")
    )
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "services/provider_bookings.html", {"page": page})


@login_required
def submit_review(request, service_id: int):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    if request.user.is_provider:
        messages.error(request, "Providers cannot submit reviews.")
        return redirect("service_detail", pk=service.id)
    if request.method != "POST":
        return redirect("service_detail", pk=service.id)

    rating_raw = request.POST.get("rating", "").strip()
    comment = (request.POST.get("comment", "") or "").strip()
    try:
        rating = int(rating_raw)
    except ValueError:
        messages.error(request, "Invalid rating.")
        return redirect("service_detail", pk=service.id)

    if rating < 1 or rating > 5 or not comment:
        messages.error(request, "Please provide a rating (1-5) and comment.")
        return redirect("service_detail", pk=service.id)

    Review.objects.create(service=service, customer=request.user, rating=rating, comment=comment)
    messages.success(request, "Review submitted. Thank you!")
    return redirect("service_detail", pk=service.id)


@login_required
def subscription_plans(request):
    if not request.user.is_provider:
        raise Http404()
    plans = SubscriptionPlan.objects.all()
    active_subscription = _provider_active_subscription(request.user)
    return render(
        request,
        "services/subscription_plans.html",
        {"plans": plans, "active_subscription": active_subscription},
    )


@login_required
def subscribe(request, plan_id: int):
    if not request.user.is_provider:
        raise Http404()
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    ProviderSubscription.objects.filter(provider=request.user, active=True).update(active=False)
    ProviderSubscription.objects.create(provider=request.user, plan=plan, active=True)
    messages.success(request, f"Subscription activated: {plan.name}.")
    return redirect("provider_dashboard")


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        raise Http404()

    context = {
        "users": User.objects.count(),
        "services": Service.objects.count(),
        "bookings": Booking.objects.count(),
        "providers": User.objects.filter(role=User.Role.PROVIDER).count(),
    }
    return render(request, "services/admin_dashboard.html", context)


@login_required
def pay_service_mobile_money(request, service_id: int):
    service = get_object_or_404(Service.objects.select_related("provider"), pk=service_id, is_active=True)
    if request.user.is_provider:
        messages.error(request, "Providers cannot pay for their own marketplace services.")
        return redirect("service_detail", pk=service.id)
    if request.method != "POST":
        return redirect("service_detail", pk=service.id)

    phone = (request.POST.get("phone") or "").strip()
    network = (request.POST.get("network") or "").strip()
    amount_raw = (request.POST.get("amount") or "").strip()

    try:
        amount = float(amount_raw) if amount_raw else float(service.price)
    except ValueError:
        messages.error(request, "Invalid payment amount.")
        return redirect("service_detail", pk=service.id)

    if not phone or network not in {ServicePayment.Network.MTN, ServicePayment.Network.TELECEL, ServicePayment.Network.AT}:
        messages.error(request, "Please provide a valid MoMo number and network.")
        return redirect("service_detail", pk=service.id)

    payment = ServicePayment.objects.create(
        customer=request.user,
        provider=service.provider,
        service=service,
        amount=amount,
        phone=phone,
        network=network,
        reference=f"SERV-{uuid4().hex[:10].upper()}",
        status=ServicePayment.Status.PENDING,
    )

    # Placeholder flow: mark as successful immediately until payment gateway is integrated.
    payment.status = ServicePayment.Status.SUCCESS
    payment.save(update_fields=["status", "updated_at"])

    create_notification(
        user=request.user,
        title="Payment successful",
        message=f"MoMo payment received for {service.name}. Ref: {payment.reference}",
        link=reverse("service_detail", kwargs={"pk": service.id}),
    )
    create_notification(
        user=service.provider,
        title="New payment received",
        message=f"{request.user.username} paid GHS {payment.amount:.2f} for {service.name}. Ref: {payment.reference}",
        link="/provider/bookings/",
    )

    messages.success(request, f"Payment successful (placeholder). Reference: {payment.reference}")
    return redirect("service_detail", pk=service.id)


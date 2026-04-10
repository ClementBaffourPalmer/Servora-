from datetime import date, time

from django.test import TestCase

from accounts.models import User
from bookings.models import Booking
from services.models import Service, ServiceCategory


class BookingLifecycleTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(username="provider1", password="pass1234", role=User.Role.PROVIDER)
        self.customer = User.objects.create_user(username="customer1", password="pass1234", role=User.Role.CUSTOMER)
        self.category, _ = ServiceCategory.objects.get_or_create(name="Laundry", defaults={"slug": "laundry"})
        self.service = Service.objects.create(
            provider=self.provider,
            category=self.category,
            name="Wash and Fold",
            price="50.00",
            is_active=True,
        )
        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            date=date.today(),
            time=time(hour=10, minute=0),
            contact_name="John Doe",
            contact_phone="233240000000",
        )

    def test_mark_paid_sets_confirmation_and_code(self):
        self.booking.mark_paid("TX-REF-1", "card")
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.paid)
        self.assertEqual(self.booking.status, Booking.Status.CONFIRMED)
        self.assertTrue(self.booking.booking_code.startswith("SVR-"))

    def test_check_in_and_complete_guards(self):
        self.assertFalse(self.booking.can_check_in())
        self.booking.mark_paid("TX-REF-2", "mobilemoneyghana")
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.can_check_in())
        self.booking.checked_in = True
        self.booking.save(update_fields=["checked_in"])
        self.assertTrue(self.booking.can_complete())

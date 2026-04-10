from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import ProviderProfile, User
from services.models import Service, ServiceCategory


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class MarketplaceSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        provider = User.objects.create_user(username="cleanqueen", password="pass1234", role=User.Role.PROVIDER)
        profile, _ = ProviderProfile.objects.get_or_create(user=provider)
        profile.business_name = "Clean Queen Co"
        profile.display_name = "Aba"
        profile.save()
        cat, _ = ServiceCategory.objects.get_or_create(name="Laundry", defaults={"slug": "laundry"})
        Service.objects.create(
            provider=provider,
            category=cat,
            name="Premium Wash",
            price="30.00",
            is_active=True,
        )

    def test_search_matches_provider_business_and_service(self):
        response = self.client.get(reverse("home"), {"q": "queen"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Premium Wash")

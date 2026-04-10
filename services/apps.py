from django.apps import AppConfig
from django.db.models.signals import post_migrate
from pathlib import Path
import shutil


def _seed_categories(sender, **kwargs):
    from .models import Service, ServiceCategory  # noqa: WPS433

    defaults = [
        "Nail Technician",
        "Wig & Frontals",
        "Hair Salon",
        "Barbering",
        "Laundry",
        "Welding",
    ]
    # Remove unrelated demo data and cleanup deprecated categories when unused.
    deprecated_categories = ["Laundry Services", "Electric Welding", "Wig & Frontal Sales"]
    Service.objects.filter(category__name__in=deprecated_categories).delete()
    for deprecated in deprecated_categories:
        category = ServiceCategory.objects.filter(name=deprecated).first()
        if category and not category.services.exists():
            category.delete()
    for name in defaults:
        ServiceCategory.objects.get_or_create(name=name)


def _seed_demo_services(sender, **kwargs):
    """
    Seed dummy services requested for realistic preview.
    - Creates a demo provider account (unusable password)
    - Creates the example services under that provider
    """
    from accounts.models import ProviderProfile, User  # noqa: WPS433

    from .models import Service, ServiceCategory  # noqa: WPS433

    demo_provider, created = User.objects.get_or_create(
        username="demo_provider",
        defaults={"email": "demo@servora.local", "role": User.Role.PROVIDER},
    )
    if created:
        demo_provider.set_unusable_password()
        demo_provider.save(update_fields=["password"])
    ProviderProfile.objects.get_or_create(
        user=demo_provider, defaults={"display_name": "Servora Demo Provider"}
    )

    catalog = {
        "Nail Technician": [
            ("Gel Manicure", "Long-lasting glossy manicure with gel finish.", 120, "gel-manicure.jpg"),
            ("Acrylic Nails", "Custom acrylic extensions with shape and design.", 180, "acrylic-nails.jpg"),
            ("Pedicure", "Relaxing foot care with polish and exfoliation.", 140, "pedicure.jpg"),
        ],
        "Wig & Frontals": [
            ("Lace Front Installation", "Natural-looking lace install with secure fitting.", 220, "lace-front-installation.jpg"),
            ("Frontal Styling", "Professional frontal styling and finishing.", 170, "frontal-styling.jpg"),
            ("Wig Revamp", "Revive old wigs with washing, treatment, and styling.", 160, "wig-revamp.jpg"),
        ],
        "Hair Salon": [
            ("Hair Braiding", "Creative protective braiding styles tailored to you.", 200, "hair-braiding.jpg"),
            ("Hair Wash", "Deep cleansing and scalp refresh service.", 90, "hair-wash.jpg"),
            ("Hair Treatment", "Moisture and repair treatment for healthier hair.", 150, "hair-treatment.jpg"),
        ],
        "Barbering": [
            ("Haircut", "Sharp modern cuts and classic barber styles.", 100, "haircut.jpg"),
            ("Beard Grooming", "Trim, shape, and style your beard professionally.", 80, "beard-grooming.jpg"),
            ("Hairline Fix", "Precision hairline shaping for a clean look.", 70, "hairline-fix.jpg"),
        ],
    }

    base_dir = Path(__file__).resolve().parent.parent
    static_service_dir = base_dir / "static" / "images" / "services"
    media_service_dir = base_dir / "media" / "services"
    media_service_dir.mkdir(parents=True, exist_ok=True)

    allowed_names = {name for items in catalog.values() for name, *_ in items}
    Service.objects.filter(provider=demo_provider).exclude(name__in=allowed_names).delete()

    for category_name, items in catalog.items():
        category = ServiceCategory.objects.get(name=category_name)
        for name, desc, price, filename in items:
            src = static_service_dir / filename
            dst = media_service_dir / filename
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
            Service.objects.update_or_create(
                provider=demo_provider,
                name=name,
                defaults={
                    "category": category,
                    "description": desc,
                    "price": price,
                    "image": f"services/{filename}",
                    "image_url": "",
                    "is_active": True,
                },
            )

    # Ensure existing services also point to local media images using category+name mapping.
    for category_name, items in catalog.items():
        for service_name, _desc, _price, filename in items:
            Service.objects.filter(
                category__name=category_name,
                name=service_name,
            ).update(image=f"services/{filename}", image_url="")


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"

    def ready(self):
        post_migrate.connect(_seed_categories, sender=self)
        post_migrate.connect(_seed_demo_services, sender=self)


from accounts.models import User

from .models import Service


def ensure_provider_has_starter_services(provider: User) -> None:
    """
    If a provider has no services, copy the demo catalog into their account
    so provider pages have realistic preview content.
    """
    if not getattr(provider, "is_provider", False):
        return
    if Service.objects.filter(provider=provider).exists():
        return

    demo = User.objects.filter(username="demo_provider").first()
    if not demo:
        return

    demo_services = Service.objects.filter(provider=demo, is_active=True).select_related("category")
    for s in demo_services:
        kwargs = {
            "provider": provider,
            "category": s.category,
            "name": s.name,
            "description": s.description,
            "price": s.price,
            "image_url": "",
            "is_active": True,
        }
        if s.image and s.image.name:
            kwargs["image"] = s.image.name
        Service.objects.create(**kwargs)


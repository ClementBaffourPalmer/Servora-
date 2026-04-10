"""
Templates: prefer uploaded media; fall back to bundled static images (works offline).
"""
from __future__ import annotations

from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

# Local filenames under static/images/services/ and media/services/
SERVICE_STATIC_BY_CATEGORY_AND_NAME: dict[tuple[str, str], str] = {
    ("Nail Technician", "Gel Manicure"): "gel-manicure.jpg",
    ("Nail Technician", "Acrylic Nails"): "acrylic-nails.jpg",
    ("Nail Technician", "Pedicure"): "pedicure.jpg",
    ("Wig & Frontals", "Lace Front Installation"): "lace-front-installation.jpg",
    ("Wig & Frontals", "Frontal Styling"): "frontal-styling.jpg",
    ("Wig & Frontals", "Wig Revamp"): "wig-revamp.jpg",
    ("Hair Salon", "Hair Braiding"): "hair-braiding.jpg",
    ("Hair Salon", "Hair Wash"): "hair-wash.jpg",
    ("Hair Salon", "Hair Treatment"): "hair-treatment.jpg",
    ("Barbering", "Haircut"): "haircut.jpg",
    ("Barbering", "Beard Grooming"): "beard-grooming.jpg",
    ("Barbering", "Hairline Fix"): "hairline-fix.jpg",
}

CATEGORY_DEFAULT_STATIC: dict[str, str] = {
    "Nail Technician": "gel-manicure.jpg",
    "Wig & Frontals": "lace-front-installation.jpg",
    "Hair Salon": "hair-braiding.jpg",
    "Barbering": "haircut.jpg",
}

DEFAULT_STATIC = "images/services/gel-manicure.jpg"


@register.simple_tag
def service_display_image_url(service) -> str:
    """
    Return a URL that always resolves in dev and prod:
    - Use ImageField URL only if the file exists on disk (avoids broken <img>).
    - Otherwise use the matching file under static/images/services/.
    """
    if service is None:
        return static(DEFAULT_STATIC)

    version = ""
    updated_at = getattr(service, "updated_at", None)
    if updated_at:
        version = f"?v={int(updated_at.timestamp())}"

    if getattr(service, "image", None) and service.image.name:
        path = Path(settings.MEDIA_ROOT) / service.image.name
        if path.is_file():
            return f"{service.image.url}{version}"

    category_name = getattr(getattr(service, "category", None), "name", "")
    filename = SERVICE_STATIC_BY_CATEGORY_AND_NAME.get((category_name, service.name))
    if not filename:
        filename = CATEGORY_DEFAULT_STATIC.get(category_name)
    if filename:
        return f"{static(f'images/services/{filename}')}{version}"
    return f"{static(DEFAULT_STATIC)}{version}"

from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from services.models import Service

CATALOG = {
    "Nail Technician": [
        ("Gel Manicure", "gel-manicure.jpg"),
        ("Acrylic Nails", "acrylic-nails.jpg"),
        ("Pedicure", "pedicure.jpg"),
    ],
    "Wig & Frontals": [
        ("Lace Front Installation", "lace-front-installation.jpg"),
        ("Frontal Styling", "frontal-styling.jpg"),
        ("Wig Revamp", "wig-revamp.jpg"),
    ],
    "Hair Salon": [
        ("Hair Braiding", "hair-braiding.jpg"),
        ("Hair Wash", "hair-wash.jpg"),
        ("Hair Treatment", "hair-treatment.jpg"),
    ],
    "Barbering": [
        ("Haircut", "haircut.jpg"),
        ("Beard Grooming", "beard-grooming.jpg"),
        ("Hairline Fix", "hairline-fix.jpg"),
    ],
}


class Command(BaseCommand):
    help = "Copy local static service images to MEDIA and relink services to local files."

    def handle(self, *args, **kwargs):
        base_dir = Path(settings.BASE_DIR)
        static_dir = base_dir / "static" / "images" / "services"
        media_dir = Path(settings.MEDIA_ROOT) / "services"
        media_dir.mkdir(parents=True, exist_ok=True)

        for items in CATALOG.values():
            for _service_name, filename in items:
                src = static_dir / filename
                dst = media_dir / filename
                if not src.is_file():
                    self.stderr.write(self.style.WARNING(f"Missing static file: {src}"))
                    continue
                if not dst.exists():
                    shutil.copy2(src, dst)
                    self.stdout.write(self.style.SUCCESS(f"Copied {filename} to media/services"))

        updated = 0
        for category_name, items in CATALOG.items():
            for service_name, filename in items:
                count = Service.objects.filter(
                    category__name=category_name,
                    name=service_name,
                ).update(image=f"services/{filename}", image_url="")
                updated += count

        self.stdout.write(self.style.SUCCESS(f"Linked {updated} service row(s) to local media images."))

import requests
from django.core.management.base import BaseCommand
from microsite.models import PontoonLocale

API = "https://pontoon.mozilla.org/api/v2/locales/"


def fetch_all_locales(url=API, timeout=30):
    """Fetch all Pontoon locales, following pagination."""
    locales = []
    while url:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        page = response.json()
        locales.extend(page.get("results", []))
        url = page.get("next")
    return locales


class Command(BaseCommand):
    help = "Synchronize locales from Pontoon into the PontoonLocale model"

    def handle(self, *args, **options):
        data = fetch_all_locales()
        created = updated = 0

        for item in data:
            code = item["code"]
            name = item.get("name") or code
            obj, was_created = PontoonLocale.objects.update_or_create(code=code, defaults={"name": name})
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {len(data)} locales — {created} new, {updated} updated."))

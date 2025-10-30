import requests
from django.core.management.base import BaseCommand
from microsite.models import PontoonLocale, PontoonProject


def fetch_data(url, timeout=30):
    """Fetch data from Pontoon API."""
    data = []

    while url:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        page = response.json()
        data.extend(page.get("results", []))
        url = page.get("next")

    return data


class Command(BaseCommand):
    help = "Synchronize data from Pontoon into data model"

    def handle(self, *args, **options):
        LOCALES_API = "https://pontoon.mozilla.org/api/v2/locales/"
        locales = fetch_data(LOCALES_API)
        created = updated = 0

        for item in locales:
            code = item["code"]
            name = item.get("name") or code
            _, was_created = PontoonLocale.objects.update_or_create(code=code, defaults={"name": name})
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {len(locales)} locales — {created} new, {updated} updated."))

        PROJECTS_API = "https://pontoon.mozilla.org/api/v2/projects/?include_disabled=true"
        projects = fetch_data(PROJECTS_API)
        created = updated = 0

        for item in projects:
            slug = item["slug"]
            name = item.get("name") or slug
            disabled = item.get("disabled", False)
            _, was_created = PontoonProject.objects.update_or_create(slug=slug, defaults={"name": name, "disabled": disabled})
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {len(projects)} projects — {created} new, {updated} updated."))
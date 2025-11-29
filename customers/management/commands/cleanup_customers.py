from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from django.conf import settings
from customers.models import Customer


class Command(BaseCommand):
    help = "Delete customers older than RETENTION_DAYS (hard delete)."

    def handle(self, *args, **options):
        days = int(settings.RETENTION_DAYS)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        qs = Customer.objects.filter(created_at__lt=cutoff)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} customers older than {days} days."))

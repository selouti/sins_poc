from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction

from customers.models import Customer, FieldDefinition


class Command(BaseCommand):
    help = "Load sample data fixtures for customers and field definitions (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--extras", type=int, default=0, help="Optional: create N extra demo customers.")

    @transaction.atomic
    def handle(self, *args, **options):
        created_any = False

        # Ensure FieldDefinitions exist
        if FieldDefinition.objects.count() == 0:
            self.stdout.write("Loading field definitions fixture...")
            call_command("loaddata", "customers/fixtures/fields.json", verbosity=0)
            created_any = True

        # Ensure Customers exist
        if Customer.objects.count() == 0:
            self.stdout.write("Loading customers fixture...")
            call_command("loaddata", "customers/fixtures/customers.json", verbosity=0)
            created_any = True

        # Optional extras
        extras = int(options.get("extras") or 0)
        if extras > 0:
            self._create_extras(extras)
            created_any = True

        if created_any:
            self.stdout.write(self.style.SUCCESS("Sample data loaded."))
        else:
            self.stdout.write(self.style.WARNING("Sample data already present; no changes."))

    def _create_extras(self, n: int):
        base = Customer.objects.count()
        for i in range(1, n + 1):
            Customer.objects.create(
                surname=f"Demo{i}",
                name=f"User{i}",
                document_number=f"DEMO-{base + i:06d}",
                extra_fields={"notes": "generated"},
            )
        self.stdout.write(self.style.SUCCESS(f"Created {n} extra demo customers."))

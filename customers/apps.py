import os
import sys
from django.apps import AppConfig
from django.db import connection


class CustomersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customers"

    def ready(self):  # pragma: no cover - startup utility
        # Allow auto sample-data loading when env var is set, even outside Docker.
        val = os.environ.get("LOAD_SAMPLE_DATA") or os.environ.get("load_sample_data")
        if not val:
            return
        if str(val).lower() not in {"1", "true", "yes", "on"}:
            return

        # Avoid interfering with management commands that set up DB.
        if len(sys.argv) > 1 and sys.argv[1] in {
            "migrate",
            "makemigrations",
            "collectstatic",
            "loaddata",
            "shell",
            "createsuperuser",
            "load_sample_data",
            "cleanup_customers",
            "consume_events",
            "test",
        }:
            return

        try:
            tables = set(connection.introspection.table_names())
            # Only attempt after core tables exist
            if {"customers_customer", "customers_fielddefinition"}.issubset(tables):
                from customers.models import Customer, FieldDefinition
                if Customer.objects.count() == 0 and FieldDefinition.objects.count() == 0:
                    from django.core.management import call_command
                    call_command("load_sample_data")
        except Exception:
            # Silent no-op if DB not ready yet
            return

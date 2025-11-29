import json
import logging
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from audit.models import AppliedEvent
from customers.models import Customer

logger = logging.getLogger(__name__)

try:
    from kafka import KafkaConsumer
except Exception:  # pragma: no cover
    KafkaConsumer = None  # type: ignore


class Command(BaseCommand):
    help = "Consume Kafka events to sync customers across locations"

    def _connect_with_retry(self, max_wait: int = 60):
        if KafkaConsumer is None:
            self.stdout.write(self.style.WARNING("Kafka not available; exiting consumer."))
            return None
        delay = 1.0
        total = 0.0
        while True:
            try:
                consumer = KafkaConsumer(
                    "customer.events",
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP,
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id=f"sins_consumer_{settings.LOCATION_ID}",
                )
                return consumer
            except Exception as e:  # pragma: no cover
                logger.warning("Kafka consumer connect failed (%s). Retrying in %.1fs", e, delay)
                time.sleep(delay)
                total += delay
                delay = min(delay * 2, 10.0)
                if total >= max_wait:
                    # keep retrying, but log less frequently
                    total = 0.0

    def handle(self, *args, **options):
        consumer = self._connect_with_retry()
        if consumer is None:
            return
        self.stdout.write(self.style.SUCCESS("Consumer started"))
        for msg in consumer:
            evt = msg.value
            event_id = evt.get("event_id")
            if not event_id:
                continue
            if AppliedEvent.objects.filter(event_id=event_id).exists():
                continue
            try:
                self.apply_event(evt)
                AppliedEvent.objects.create(event_id=event_id)
            except Exception as e:  # pragma: no cover
                logger.exception("Failed to apply event %s: %s", event_id, e)

    def apply_event(self, evt):
        etype = evt.get("event_type")
        payload = evt.get("payload") or {}
        eid = evt.get("entity_id")
        if etype == "customer_created" or etype == "customer_updated":
            fields = {k: payload.get(k) for k in ["surname", "name", "dob", "document_number", "extra_fields"]}
            Customer.objects.update_or_create(id=eid, defaults=fields)
        elif etype == "customer_deleted":
            try:
                Customer.objects.filter(id=eid).update(deleted_at=__import__('datetime').datetime.utcnow())
            except Exception:
                pass

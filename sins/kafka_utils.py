import json
import logging
import os
from typing import Any, Dict

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover
    KafkaProducer = None  # type: ignore


_producer = None
_last_error = None


def get_producer():
    global _producer
    if _producer is None and KafkaProducer is not None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except Exception as e:  # pragma: no cover
            # Do not permanently disable; allow future retries on next call
            logger.warning("Kafka unavailable: %s", e)
            _producer = None
    return _producer


def emit_event(topic: str, event_id: str, event_type: str, entity_id: str, location_id: str, payload: Dict[str, Any]):
    producer = get_producer()
    message = {
        "event_id": event_id,
        "event_type": event_type,
        "entity_id": entity_id,
        "location_id": location_id,
        "payload": payload,
    }
    if producer is None:
        logger.info("kafka.emit.skipped topic=%s event_type=%s", topic, event_type)
        return
    try:
        producer.send(topic, message)
        producer.flush(1.0)
        logger.info("kafka.emit topic=%s event_type=%s", topic, event_type)
    except Exception as e:  # pragma: no cover
        logger.warning("Kafka emit failed: %s", e)

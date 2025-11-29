from django.db import models


class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    actor_role = models.CharField(max_length=50, blank=True)
    action = models.CharField(max_length=50)
    entity = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    location_id = models.CharField(max_length=50, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["entity", "entity_id"]),
        ]
        ordering = ["-timestamp"]


class AppliedEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]

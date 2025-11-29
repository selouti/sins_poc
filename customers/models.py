from django.db import models
from django.contrib.postgres.fields import ArrayField  # optional if moving to Postgres later
try:
    from django.db.models import JSONField  # Django 3.1+
except ImportError:  # pragma: no cover
    from django.contrib.postgres.fields import JSONField  # type: ignore


class FieldDefinition(models.Model):
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} ({'active' if self.active else 'inactive'})"


class Customer(models.Model):
    surname = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    document_number = models.CharField(max_length=100, blank=True)
    extra_fields = JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["surname", "name"]),
            models.Index(fields=["document_number"]),
        ]
        ordering = ["surname", "name"]

    def __str__(self):
        return f"{self.surname}, {self.name}"

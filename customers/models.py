from django.db import models
try:
    from django.db.models import JSONField  # Django 3.1+
except ImportError:  # pragma: no cover
    from django.contrib.postgres.fields import JSONField  # type: ignore


class FieldDefinition(models.Model):
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    # Allow NULL so fixtures without explicit timestamps can load cleanly
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

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

    # Allow NULL so fixtures without explicit timestamps can load cleanly
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["surname", "name"]),
            models.Index(fields=["document_number"]),
        ]
        ordering = ["surname", "name"]

    def __str__(self):
        return f"{self.surname}, {self.name}"

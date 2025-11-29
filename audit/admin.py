from django.contrib import admin
from .models import AuditLog, AppliedEvent


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor_role", "action", "entity", "entity_id", "location_id")
    search_fields = ("actor_role", "action", "entity", "entity_id", "location_id")
    list_filter = ("action", "entity", "location_id")


@admin.register(AppliedEvent)
class AppliedEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "applied_at")
    search_fields = ("event_id",)

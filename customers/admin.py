from django.contrib import admin
from .models import Customer, FieldDefinition


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "surname", "name", "document_number", "created_at", "deleted_at")
    search_fields = ("surname", "name", "document_number")


@admin.register(FieldDefinition)
class FieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "label", "active", "created_at")
    list_filter = ("active",)
    search_fields = ("key", "label")

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Cupon, Employee, Organization, Lead


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "start_code",
        "channel_id",
        "uzoman_channel_id",
        "is_default",
        "created_at",
    )
    list_filter = ("is_default", "created_at")
    search_fields = ("name", "start_code", "channel_id", "uzoman_channel_id")
    ordering = ("-created_at", "-id")


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ("id", "name", "user_id", "active_organization")
    list_filter = ("active_organization", "organizations")
    search_fields = (
        "name",
        "user_id",
        "active_organization__name",
        "active_organization__start_code",
        "organizations__name",
        "organizations__start_code",
    )
    ordering = ("name", "id")
    autocomplete_fields = ("active_organization", "organizations")
    list_select_related = ("active_organization",)


@admin.register(Cupon)
class CuponAdmin(ModelAdmin):
    list_display = ("id", "date", "checked", "name", "user_id", "organization")
    list_filter = ("organization", "checked", "date")
    search_fields = ("name", "user_id", "organization__name", "organization__start_code")
    ordering = ("-date", "-id")
    autocomplete_fields = ("organization",)
    list_select_related = ("organization",)


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ("id", "created_at", "contact_name", "phone")
    list_filter = ("created_at",)
    search_fields = ("contact_name", "phone")
    ordering = ("-created_at", "-id")
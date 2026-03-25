from django.contrib import admin

from .models import Cupon, Employee, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
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
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user_id", "organization")
    list_filter = ("organization",)
    search_fields = ("name", "user_id", "organization__name", "organization__start_code")
    ordering = ("organization", "name", "id")
    autocomplete_fields = ("organization",)
    list_select_related = ("organization",)


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "checked", "name", "user_id", "organization")
    list_filter = ("organization", "checked", "date")
    search_fields = ("name", "user_id", "organization__name", "organization__start_code")
    ordering = ("-date", "-id")
    autocomplete_fields = ("organization",)
    list_select_related = ("organization",)
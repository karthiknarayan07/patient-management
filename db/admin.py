from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Ambulance,
    Emergency,
    EmergencyContact,
    Hospital,
    MedicalRecord,
    Notification,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_elderly",
        "is_active",
    )
    list_filter = ("is_elderly", "is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Personal Information",
            {
                "fields": (
                    "phone_number",
                    "date_of_birth",
                    "address",
                    "profile_picture",
                    "is_elderly",
                )
            },
        ),
        ("Location", {"fields": ("latitude", "longitude")}),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                    "emergency_contact_address",
                )
            },
        ),
        (
            "Medical Information",
            {
                "fields": (
                    "blood_group",
                    "medical_conditions",
                    "medications",
                    "medical_notes",
                )
            },
        ),
    )


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    """Admin configuration for Hospital model"""

    list_display = (
        "name",
        "city",
        "state",
        "has_emergency_services",
        "available_ambulances",
        "is_active",
    )
    list_filter = (
        "city",
        "state",
        "has_emergency_services",
        "has_ambulance",
        "operates_24x7",
        "is_active",
    )
    search_fields = ("name", "registration_number", "city", "specializations")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Emergency)
class EmergencyAdmin(admin.ModelAdmin):
    """Admin configuration for Emergency model"""

    list_display = ("patient", "priority", "status", "assigned_hospital", "created_at")
    list_filter = ("priority", "status", "created_at", "assigned_hospital")
    search_fields = ("patient__first_name", "patient__last_name", "description")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("patient", "assigned_hospital")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model"""

    list_display = (
        "title",
        "notification_type",
        "recipient_type",
        "status",
        "created_at",
    )
    list_filter = ("notification_type", "recipient_type", "status", "created_at")
    search_fields = ("title", "message")
    readonly_fields = ("created_at", "updated_at", "sent_at", "delivered_at", "read_at")
    raw_id_fields = ("hospital", "user", "emergency")


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Admin configuration for MedicalRecord model"""

    list_display = ("patient", "record_type", "doctor_name", "visit_date", "hospital")
    list_filter = ("record_type", "visit_date", "hospital")
    search_fields = (
        "patient__first_name",
        "patient__last_name",
        "diagnosis",
        "doctor_name",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("patient", "hospital")


@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    """Admin configuration for Ambulance model"""

    list_display = ("vehicle_number", "hospital", "driver_name", "status")
    list_filter = (
        "status",
        "hospital",
        "has_ventilator",
        "has_defibrillator",
        "has_oxygen",
    )
    search_fields = ("vehicle_number", "driver_name", "hospital__name")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("hospital", "current_emergency")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    """Admin configuration for EmergencyContact model"""

    list_display = ("name", "patient", "relationship", "phone_number", "is_primary")
    list_filter = ("relationship", "is_primary")
    search_fields = (
        "name",
        "phone_number",
        "patient__first_name",
        "patient__last_name",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("patient",)

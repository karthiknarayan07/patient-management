import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from geopy.distance import geodesic


class BaseModel(models.Model):
    """
    Base model with common fields for all models
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    Extended User model for elderly patients
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Personal Information
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField()

    # Location for emergency services
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relationship = models.CharField(max_length=50)
    emergency_contact_address = models.TextField(blank=True)

    # Medical Information
    blood_group = models.CharField(max_length=5, blank=True)
    medical_conditions = models.TextField(
        blank=True, help_text="Chronic conditions, allergies, etc."
    )
    medications = models.TextField(blank=True, help_text="Current medications")
    medical_notes = models.TextField(blank=True)

    # Profile
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    is_elderly = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def get_location(self):
        """Return user's location as tuple (latitude, longitude)"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None

    class Meta:
        db_table = "users"


class Hospital(BaseModel):
    """
    Hospital model with location and ambulance services
    """

    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, unique=True)

    # Contact Information
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)

    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Location coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)

    # Services
    has_emergency_services = models.BooleanField(default=True)
    has_ambulance = models.BooleanField(default=True)
    total_ambulances = models.PositiveIntegerField(default=1)
    available_ambulances = models.PositiveIntegerField(default=1)

    # Specializations
    specializations = models.TextField(
        help_text="Comma-separated list of medical specializations"
    )

    # Operating hours
    operates_24x7 = models.BooleanField(default=True)
    operating_hours = models.TextField(
        blank=True, help_text="Operating hours if not 24x7"
    )

    def __str__(self):
        return self.name

    def get_location(self):
        """Return hospital's location as tuple (latitude, longitude)"""
        return (float(self.latitude), float(self.longitude))

    def calculate_distance_to_user(self, user):
        """Calculate distance in kilometers to a user"""
        user_location = user.get_location()
        hospital_location = self.get_location()

        if user_location and hospital_location:
            return round(geodesic(user_location, hospital_location).kilometers, 2)
        return None

    def has_available_ambulance(self):
        """Check if hospital has available ambulance"""
        return self.available_ambulances > 0

    class Meta:
        ordering = ["name"]


class Emergency(BaseModel):
    """
    Emergency request model
    """

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACKNOWLEDGED", "Acknowledged"),
        ("DISPATCHED", "Ambulance Dispatched"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="emergencies"
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")

    # Emergency details
    description = models.TextField(help_text="Description of the emergency")
    location_latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    location_longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    location_address = models.TextField(blank=True)

    # Response
    assigned_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emergencies",
    )
    ambulance_dispatched_at = models.DateTimeField(null=True, blank=True)
    estimated_arrival_time = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Notes
    response_notes = models.TextField(blank=True)

    def __str__(self):
        return (
            f"Emergency #{self.id} - {self.patient.first_name} {self.patient.last_name}"
        )

    def get_emergency_location(self):
        """Get emergency location coordinates"""
        if self.location_latitude and self.location_longitude:
            return (float(self.location_latitude), float(self.location_longitude))
        return self.patient.get_location()

    def mark_ambulance_dispatched(self, hospital):
        """Mark ambulance as dispatched from hospital"""
        self.assigned_hospital = hospital
        self.status = "DISPATCHED"
        self.ambulance_dispatched_at = timezone.now()
        self.save()

        # Reduce available ambulances
        if hospital.available_ambulances > 0:
            hospital.available_ambulances -= 1
            hospital.save()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Emergencies"


class Notification(BaseModel):
    """
    Notification model for hospitals and emergency contacts
    """

    NOTIFICATION_TYPES = [
        ("EMERGENCY_ALERT", "Emergency Alert"),
        ("AMBULANCE_REQUEST", "Ambulance Request"),
        ("STATUS_UPDATE", "Status Update"),
        ("EMERGENCY_CONTACT_ALERT", "Emergency Contact Alert"),
    ]

    RECIPIENT_TYPES = [
        ("HOSPITAL", "Hospital"),
        ("EMERGENCY_CONTACT", "Emergency Contact"),
        ("USER", "User"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("DELIVERED", "Delivered"),
        ("READ", "Read"),
        ("FAILED", "Failed"),
    ]

    # Notification details
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES)
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Recipients
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )

    # Emergency contact details (when notifying emergency contact)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)

    # Related emergency
    emergency = models.ForeignKey(
        Emergency, on_delete=models.CASCADE, related_name="notifications"
    )

    # Delivery tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.notification_type} - {self.title}"

    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = "SENT"
        self.sent_at = timezone.now()
        self.save()

    def mark_as_delivered(self):
        """Mark notification as delivered"""
        self.status = "DELIVERED"
        self.delivered_at = timezone.now()
        self.save()

    def mark_as_read(self):
        """Mark notification as read"""
        self.status = "READ"
        self.read_at = timezone.now()
        self.save()

    class Meta:
        ordering = ["-created_at"]


class MedicalRecord(BaseModel):
    """
    Medical records for patients
    """

    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="medical_records"
    )
    hospital = models.ForeignKey(
        Hospital, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Record details
    record_type = models.CharField(
        max_length=50,
        choices=[
            ("EMERGENCY_VISIT", "Emergency Visit"),
            ("REGULAR_CHECKUP", "Regular Checkup"),
            ("PRESCRIPTION", "Prescription"),
            ("LAB_REPORT", "Lab Report"),
            ("DISCHARGE_SUMMARY", "Discharge Summary"),
        ],
    )

    diagnosis = models.TextField()
    treatment = models.TextField()
    medications_prescribed = models.TextField(blank=True)
    doctor_name = models.CharField(max_length=100)
    doctor_notes = models.TextField(blank=True)

    # Files
    attachments = models.FileField(upload_to="medical_records/", null=True, blank=True)

    # Visit details
    visit_date = models.DateTimeField(default=timezone.now)
    next_appointment = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.patient.first_name} {self.patient.last_name} - {self.record_type}"
        )

    class Meta:
        ordering = ["-visit_date"]


class Ambulance(BaseModel):
    """
    Ambulance tracking model
    """

    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("DISPATCHED", "Dispatched"),
        ("BUSY", "Busy"),
        ("MAINTENANCE", "Under Maintenance"),
    ]

    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name="ambulances"
    )
    vehicle_number = models.CharField(max_length=20, unique=True)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="AVAILABLE"
    )

    # Current location (updated in real-time)
    current_latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    current_longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )

    # Equipment
    has_ventilator = models.BooleanField(default=False)
    has_defibrillator = models.BooleanField(default=True)
    has_oxygen = models.BooleanField(default=True)
    equipment_notes = models.TextField(blank=True)

    # Current assignment
    current_emergency = models.ForeignKey(
        Emergency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_ambulance",
    )

    def __str__(self):
        return f"{self.vehicle_number} - {self.hospital.name}"

    def get_current_location(self):
        """Get current ambulance location"""
        if self.current_latitude and self.current_longitude:
            return (float(self.current_latitude), float(self.current_longitude))
        return None

    class Meta:
        ordering = ["hospital", "vehicle_number"]


class EmergencyContact(BaseModel):
    """
    Additional emergency contacts for patients
    """

    RELATIONSHIP_CHOICES = [
        ("SPOUSE", "Spouse"),
        ("CHILD", "Child"),
        ("PARENT", "Parent"),
        ("SIBLING", "Sibling"),
        ("FRIEND", "Friend"),
        ("CAREGIVER", "Caregiver"),
        ("NEIGHBOR", "Neighbor"),
        ("OTHER", "Other"),
    ]

    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="additional_emergency_contacts"
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    relationship = models.CharField(max_length=15, choices=RELATIONSHIP_CHOICES)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.patient.first_name} {self.patient.last_name}"

    class Meta:
        ordering = ["-is_primary", "name"]

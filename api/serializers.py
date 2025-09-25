from django.contrib.auth import authenticate
from rest_framework import serializers

from db.models import (
    Ambulance,
    Emergency,
    EmergencyContact,
    Hospital,
    MedicalRecord,
    Notification,
    User,
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "address",
            "latitude",
            "longitude",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "emergency_contact_address",
            "blood_group",
            "medical_conditions",
            "medications",
            "medical_notes",
            "profile_picture",
            "is_elderly",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "emergency_contact_name": {"required": True},
            "emergency_contact_phone": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    full_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "date_of_birth",
            "address",
            "latitude",
            "longitude",
            "location",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "emergency_contact_address",
            "blood_group",
            "medical_conditions",
            "medications",
            "medical_notes",
            "profile_picture",
            "is_elderly",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "username", "date_joined", "last_login"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_location(self, obj):
        return obj.get_location()


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include username and password")


class HospitalSerializer(serializers.ModelSerializer):
    """Serializer for hospital"""

    location = serializers.SerializerMethodField()
    distance_to_user = serializers.SerializerMethodField()
    specializations_list = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = [
            "id",
            "name",
            "registration_number",
            "phone_number",
            "email",
            "website",
            "address",
            "city",
            "state",
            "pincode",
            "latitude",
            "longitude",
            "location",
            "has_emergency_services",
            "has_ambulance",
            "total_ambulances",
            "available_ambulances",
            "specializations",
            "specializations_list",
            "operates_24x7",
            "operating_hours",
            "distance_to_user",
            "created_at",
            "updated_at",
            "is_active",
        ]

    def get_location(self, obj):
        return obj.get_location()

    def get_distance_to_user(self, obj):
        # This will be set by the view if user location is provided
        return getattr(obj, "distance_to_user", None)

    def get_specializations_list(self, obj):
        if obj.specializations:
            return [spec.strip() for spec in obj.specializations.split(",")]
        return []


class EmergencySerializer(serializers.ModelSerializer):
    """Serializer for emergency requests"""

    patient_name = serializers.SerializerMethodField()
    patient_phone = serializers.SerializerMethodField()
    hospital_name = serializers.SerializerMethodField()
    emergency_location = serializers.SerializerMethodField()

    class Meta:
        model = Emergency
        fields = [
            "id",
            "patient",
            "patient_name",
            "patient_phone",
            "priority",
            "status",
            "description",
            "location_latitude",
            "location_longitude",
            "location_address",
            "emergency_location",
            "assigned_hospital",
            "hospital_name",
            "ambulance_dispatched_at",
            "estimated_arrival_time",
            "completed_at",
            "response_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_patient_phone(self, obj):
        return obj.patient.phone_number

    def get_hospital_name(self, obj):
        return obj.assigned_hospital.name if obj.assigned_hospital else None

    def get_emergency_location(self, obj):
        return obj.get_emergency_location()


class EmergencyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating emergency requests"""

    class Meta:
        model = Emergency
        fields = [
            "priority",
            "description",
            "location_latitude",
            "location_longitude",
            "location_address",
        ]

    def create(self, validated_data):
        # Patient will be set from the authenticated user in the view
        validated_data["patient"] = self.context["request"].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""

    hospital_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    emergency_description = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "recipient_type",
            "status",
            "title",
            "message",
            "hospital",
            "hospital_name",
            "user",
            "user_name",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency",
            "emergency_description",
            "sent_at",
            "delivered_at",
            "read_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None

    def get_emergency_description(self, obj):
        return obj.emergency.description if obj.emergency else None


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for medical records"""

    patient_name = serializers.SerializerMethodField()
    hospital_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient",
            "patient_name",
            "hospital",
            "hospital_name",
            "record_type",
            "diagnosis",
            "treatment",
            "medications_prescribed",
            "doctor_name",
            "doctor_notes",
            "attachments",
            "visit_date",
            "next_appointment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None


class AmbulanceSerializer(serializers.ModelSerializer):
    """Serializer for ambulance"""

    hospital_name = serializers.SerializerMethodField()
    current_location = serializers.SerializerMethodField()
    current_emergency_description = serializers.SerializerMethodField()

    class Meta:
        model = Ambulance
        fields = [
            "id",
            "hospital",
            "hospital_name",
            "vehicle_number",
            "driver_name",
            "driver_phone",
            "status",
            "current_latitude",
            "current_longitude",
            "current_location",
            "has_ventilator",
            "has_defibrillator",
            "has_oxygen",
            "equipment_notes",
            "current_emergency",
            "current_emergency_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_hospital_name(self, obj):
        return obj.hospital.name

    def get_current_location(self, obj):
        return obj.get_current_location()

    def get_current_emergency_description(self, obj):
        if obj.current_emergency:
            return obj.current_emergency.description
        return None


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for emergency contacts"""

    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "patient",
            "patient_name",
            "name",
            "phone_number",
            "email",
            "relationship",
            "address",
            "is_primary",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "patient", "created_at", "updated_at"]

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"


class EmergencyResponseSerializer(serializers.Serializer):
    """Serializer for hospital emergency response"""

    emergency_id = serializers.UUIDField()
    estimated_arrival_minutes = serializers.IntegerField(min_value=1, max_value=120)
    response_notes = serializers.CharField(max_length=1000, required=False)


class NearbyHospitalsSerializer(serializers.Serializer):
    """Serializer for finding nearby hospitals"""

    latitude = serializers.DecimalField(max_digits=10, decimal_places=8)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8)
    radius_km = serializers.IntegerField(min_value=1, max_value=50, default=10)
    emergency_services_only = serializers.BooleanField(default=True)
    available_ambulance_only = serializers.BooleanField(default=True)


class EmergencyStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating emergency status"""

    status = serializers.ChoiceField(choices=Emergency.STATUS_CHOICES)
    response_notes = serializers.CharField(max_length=1000, required=False)
    estimated_arrival_time = serializers.DateTimeField(required=False)

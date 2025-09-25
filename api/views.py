"""
API Views for Elderly Healthcare System
"""

from django.contrib.auth import login, logout
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from db.models import (
    Ambulance,
    Emergency,
    EmergencyContact,
    Hospital,
    MedicalRecord,
    Notification,
    User,
)

from .serializers import (
    AmbulanceSerializer,
    EmergencyContactSerializer,
    EmergencyCreateSerializer,
    EmergencyResponseSerializer,
    EmergencySerializer,
    EmergencyStatusUpdateSerializer,
    HospitalSerializer,
    LoginSerializer,
    MedicalRecordSerializer,
    NearbyHospitalsSerializer,
    NotificationSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .utils import (
    create_emergency_notifications,
    dispatch_ambulance,
    find_nearby_hospitals,
    mark_emergency_completed,
    send_status_update_notifications,
)


class AuthViewSet(viewsets.GenericViewSet):
    """Authentication ViewSet"""

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """User registration"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "token": token.key,
                    "message": "Registration successful",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="login")
    def login_user(self, request):
        """User login"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "token": token.key,
                    "message": "Login successful",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="logout")
    def logout_user(self, request):
        """User logout"""
        if request.user.is_authenticated:
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                pass
            logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """User management ViewSet"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    ordering_fields = ["first_name", "last_name", "date_joined"]
    filterset_fields = ["is_elderly", "is_active"]

    def get_queryset(self):
        """Return users based on permissions"""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=["get"], url_path="profile")
    def get_profile(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="update-profile")
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="emergency-history")
    def emergency_history(self, request, pk=None):
        """Get user's emergency history"""
        user = self.get_object()
        emergencies = user.emergencies.all()
        serializer = EmergencySerializer(emergencies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="medical-records")
    def medical_records(self, request, pk=None):
        """Get user's medical records"""
        user = self.get_object()
        records = user.medical_records.all()
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)


class HospitalViewSet(viewsets.ModelViewSet):
    """Hospital management ViewSet"""

    queryset = Hospital.objects.filter(is_active=True)
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "city", "specializations"]
    ordering_fields = ["name", "city", "created_at"]
    filterset_fields = [
        "city",
        "state",
        "has_emergency_services",
        "has_ambulance",
        "operates_24x7",
    ]

    @action(detail=False, methods=["post"], url_path="nearby")
    def nearby_hospitals(self, request):
        """Find nearby hospitals"""
        serializer = NearbyHospitalsSerializer(data=request.data)
        if serializer.is_valid():
            hospitals = find_nearby_hospitals(
                latitude=serializer.validated_data["latitude"],
                longitude=serializer.validated_data["longitude"],
                radius_km=serializer.validated_data.get("radius_km", 10),
                emergency_services_only=serializer.validated_data.get(
                    "emergency_services_only", True
                ),
                available_ambulance_only=serializer.validated_data.get(
                    "available_ambulance_only", True
                ),
            )
            hospital_serializer = HospitalSerializer(hospitals, many=True)
            return Response(
                {"hospitals": hospital_serializer.data, "count": len(hospitals)}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="ambulances")
    def hospital_ambulances(self, request, pk=None):
        """Get hospital's ambulances"""
        hospital = self.get_object()
        ambulances = hospital.ambulances.all()
        serializer = AmbulanceSerializer(ambulances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="emergencies")
    def hospital_emergencies(self, request, pk=None):
        """Get hospital's emergency requests"""
        hospital = self.get_object()
        emergencies = hospital.emergencies.all()
        serializer = EmergencySerializer(emergencies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="respond-emergency")
    def respond_to_emergency(self, request, pk=None):
        """Hospital responds to emergency request"""
        hospital = self.get_object()
        serializer = EmergencyResponseSerializer(data=request.data)

        if serializer.is_valid():
            try:
                emergency = Emergency.objects.get(
                    id=serializer.validated_data["emergency_id"], status="PENDING"
                )

                success, message = dispatch_ambulance(
                    emergency=emergency,
                    hospital=hospital,
                    estimated_arrival_minutes=serializer.validated_data.get(
                        "estimated_arrival_minutes"
                    ),
                )

                if success:
                    if serializer.validated_data.get("response_notes"):
                        emergency.response_notes = serializer.validated_data[
                            "response_notes"
                        ]
                        emergency.save()

                    return Response(
                        {
                            "message": message,
                            "emergency": EmergencySerializer(emergency).data,
                        }
                    )
                else:
                    return Response(
                        {"error": message}, status=status.HTTP_400_BAD_REQUEST
                    )

            except Emergency.DoesNotExist:
                return Response(
                    {"error": "Emergency not found or already handled"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmergencyViewSet(viewsets.ModelViewSet):
    """Emergency management ViewSet"""

    queryset = Emergency.objects.all()
    serializer_class = EmergencySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["description", "patient__first_name", "patient__last_name"]
    ordering_fields = ["created_at", "priority", "status"]
    filterset_fields = ["priority", "status", "assigned_hospital"]

    def get_queryset(self):
        """Filter emergencies based on user permissions"""
        user = self.request.user
        if user.is_staff:
            return Emergency.objects.all()
        return Emergency.objects.filter(patient=user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "create":
            return EmergencyCreateSerializer
        return EmergencySerializer

    def create(self, request, *args, **kwargs):
        """Create new emergency request"""
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            emergency = serializer.save()

            # Create notifications for nearby hospitals and emergency contacts
            notifications = create_emergency_notifications(emergency)

            return Response(
                {
                    "emergency": EmergencySerializer(emergency).data,
                    "notifications_sent": len(notifications),
                    "message": f"Emergency request created. {len(notifications)} notifications sent.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Update emergency status"""
        emergency = self.get_object()
        serializer = EmergencyStatusUpdateSerializer(data=request.data)

        if serializer.is_valid():
            old_status = emergency.status
            emergency.status = serializer.validated_data["status"]

            if serializer.validated_data.get("response_notes"):
                emergency.response_notes = serializer.validated_data["response_notes"]

            if serializer.validated_data.get("estimated_arrival_time"):
                emergency.estimated_arrival_time = serializer.validated_data[
                    "estimated_arrival_time"
                ]

            emergency.save()

            # Send status update notifications
            status_message = (
                f"Emergency status updated from {old_status} to {emergency.status}."
            )
            if serializer.validated_data.get("response_notes"):
                status_message += (
                    f" Notes: {serializer.validated_data['response_notes']}"
                )

            send_status_update_notifications(emergency, status_message)

            return Response(
                {
                    "emergency": EmergencySerializer(emergency).data,
                    "message": "Status updated successfully",
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_emergency(self, request, pk=None):
        """Mark emergency as completed"""
        emergency = self.get_object()
        completion_notes = request.data.get("completion_notes", "")

        success, message = mark_emergency_completed(emergency, completion_notes)

        if success:
            return Response(
                {"emergency": EmergencySerializer(emergency).data, "message": message}
            )
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="notifications")
    def emergency_notifications(self, request, pk=None):
        """Get notifications for this emergency"""
        emergency = self.get_object()
        notifications = emergency.notifications.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    """Notification management ViewSet"""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "status"]
    filterset_fields = ["notification_type", "recipient_type", "status"]

    def get_queryset(self):
        """Filter notifications based on user"""
        user = self.request.user
        if user.is_staff:
            return Notification.objects.all()

        # Return notifications for the user or hospitals they manage
        return Notification.objects.filter(
            Q(user=user) | Q(hospital__in=user.managed_hospitals.all())
            if hasattr(user, "managed_hospitals")
            else Q(user=user)
        )

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({"message": "Notification marked as read"})

    @action(detail=False, methods=["get"], url_path="unread")
    def unread_notifications(self, request):
        """Get unread notifications"""
        unread = self.get_queryset().exclude(status="READ")
        serializer = self.get_serializer(unread, many=True)
        return Response({"notifications": serializer.data, "count": unread.count()})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = (
            self.get_queryset()
            .exclude(status="READ")
            .update(status="READ", read_at=timezone.now())
        )
        return Response({"message": f"{updated} notifications marked as read"})


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """Medical records management ViewSet"""

    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["diagnosis", "treatment", "doctor_name"]
    ordering_fields = ["visit_date", "created_at"]
    filterset_fields = ["record_type", "hospital", "patient"]

    def get_queryset(self):
        """Filter medical records based on user permissions"""
        user = self.request.user
        if user.is_staff:
            return MedicalRecord.objects.all()
        return MedicalRecord.objects.filter(patient=user)


class AmbulanceViewSet(viewsets.ModelViewSet):
    """Ambulance management ViewSet"""

    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["vehicle_number", "driver_name", "hospital__name"]
    ordering_fields = ["vehicle_number", "status", "created_at"]
    filterset_fields = ["status", "hospital", "has_ventilator", "has_defibrillator"]

    @action(detail=True, methods=["post"], url_path="update-location")
    def update_location(self, request, pk=None):
        """Update ambulance current location"""
        ambulance = self.get_object()
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if latitude and longitude:
            ambulance.current_latitude = latitude
            ambulance.current_longitude = longitude
            ambulance.save()

            return Response(
                {
                    "message": "Location updated successfully",
                    "ambulance": AmbulanceSerializer(ambulance).data,
                }
            )

        return Response(
            {"error": "Latitude and longitude are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], url_path="available")
    def available_ambulances(self, request):
        """Get available ambulances"""
        available = self.get_queryset().filter(status="AVAILABLE")
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)


class EmergencyContactViewSet(viewsets.ModelViewSet):
    """Emergency contacts management ViewSet"""

    queryset = EmergencyContact.objects.all()
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "phone_number", "relationship"]
    ordering_fields = ["name", "is_primary", "created_at"]
    filterset_fields = ["relationship", "is_primary", "patient"]

    def get_queryset(self):
        """Filter emergency contacts based on user permissions"""
        user = self.request.user
        if user.is_staff:
            return EmergencyContact.objects.all()
        return EmergencyContact.objects.filter(patient=user)

    def perform_create(self, serializer):
        """Set patient to current user when creating"""
        serializer.save(patient=self.request.user)


class DashboardAPIView(APIView):
    """Dashboard API for overview statistics"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get dashboard statistics"""
        user = request.user

        if user.is_staff:
            # Admin dashboard
            data = {
                "total_users": User.objects.count(),
                "total_hospitals": Hospital.objects.count(),
                "total_emergencies": Emergency.objects.count(),
                "active_emergencies": Emergency.objects.filter(
                    status__in=["PENDING", "ACKNOWLEDGED", "DISPATCHED", "IN_PROGRESS"]
                ).count(),
                "completed_emergencies": Emergency.objects.filter(
                    status="COMPLETED"
                ).count(),
                "available_ambulances": Ambulance.objects.filter(
                    status="AVAILABLE"
                ).count(),
                "pending_notifications": Notification.objects.filter(
                    status="PENDING"
                ).count(),
            }
        else:
            # User dashboard
            data = {
                "my_emergencies": user.emergencies.count(),
                "active_emergencies": user.emergencies.filter(
                    status__in=["PENDING", "ACKNOWLEDGED", "DISPATCHED", "IN_PROGRESS"]
                ).count(),
                "completed_emergencies": user.emergencies.filter(
                    status="COMPLETED"
                ).count(),
                "my_medical_records": user.medical_records.count(),
                "emergency_contacts": user.additional_emergency_contacts.count(),
                "unread_notifications": Notification.objects.filter(
                    user=user, status__in=["PENDING", "SENT", "DELIVERED"]
                ).count(),
            }

        return Response(data)

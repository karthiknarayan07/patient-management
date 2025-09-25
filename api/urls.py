"""
URL configuration for Elderly Healthcare System API
"""

from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import (
    AmbulanceViewSet,
    AuthViewSet,
    DashboardAPIView,
    EmergencyContactViewSet,
    EmergencyViewSet,
    HospitalViewSet,
    MedicalRecordViewSet,
    NotificationViewSet,
    UserViewSet,
)

# Create a router and register ViewSets
router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="users")
router.register(r"hospitals", HospitalViewSet, basename="hospitals")
router.register(r"emergencies", EmergencyViewSet, basename="emergencies")
router.register(r"notifications", NotificationViewSet, basename="notifications")
router.register(r"medical-records", MedicalRecordViewSet, basename="medical-records")
router.register(r"ambulances", AmbulanceViewSet, basename="ambulances")
router.register(
    r"emergency-contacts", EmergencyContactViewSet, basename="emergency-contacts"
)

app_name = "api"

urlpatterns = [
    # Router URLs
    path("", include(router.urls)),
    # Additional API endpoints
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    # Token authentication (alternative to custom auth)
    path("token-auth/", obtain_auth_token, name="token-auth"),
    # API documentation endpoints (if using drf-spectacular)
    # path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    # path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]

"""
API Endpoints Overview:

Authentication:
- POST /api/auth/register/          - User registration
- POST /api/auth/login/             - User login  
- POST /api/auth/logout/            - User logout
- POST /api/token-auth/             - Get auth token

Users:
- GET /api/users/                   - List users
- POST /api/users/                  - Create user
- GET /api/users/{id}/              - Get user details
- PUT /api/users/{id}/              - Update user
- DELETE /api/users/{id}/           - Delete user
- GET /api/users/profile/           - Get current user profile
- PATCH /api/users/update-profile/  - Update current user profile
- GET /api/users/{id}/emergency-history/ - Get user's emergency history
- GET /api/users/{id}/medical-records/   - Get user's medical records

Hospitals:
- GET /api/hospitals/               - List hospitals
- POST /api/hospitals/              - Create hospital
- GET /api/hospitals/{id}/          - Get hospital details
- PUT /api/hospitals/{id}/          - Update hospital
- DELETE /api/hospitals/{id}/       - Delete hospital
- POST /api/hospitals/nearby/       - Find nearby hospitals
- GET /api/hospitals/{id}/ambulances/ - Get hospital's ambulances
- GET /api/hospitals/{id}/emergencies/ - Get hospital's emergencies
- POST /api/hospitals/{id}/respond-emergency/ - Respond to emergency

Emergencies:
- GET /api/emergencies/             - List emergencies
- POST /api/emergencies/            - Create emergency request
- GET /api/emergencies/{id}/        - Get emergency details
- PUT /api/emergencies/{id}/        - Update emergency
- DELETE /api/emergencies/{id}/     - Delete emergency
- POST /api/emergencies/{id}/update-status/ - Update emergency status
- POST /api/emergencies/{id}/complete/      - Mark emergency as completed
- GET /api/emergencies/{id}/notifications/  - Get emergency notifications

Notifications:
- GET /api/notifications/           - List notifications
- POST /api/notifications/          - Create notification
- GET /api/notifications/{id}/      - Get notification details
- PUT /api/notifications/{id}/      - Update notification
- DELETE /api/notifications/{id}/   - Delete notification
- POST /api/notifications/{id}/mark-read/ - Mark notification as read
- GET /api/notifications/unread/    - Get unread notifications
- POST /api/notifications/mark-all-read/ - Mark all notifications as read

Medical Records:
- GET /api/medical-records/         - List medical records
- POST /api/medical-records/        - Create medical record
- GET /api/medical-records/{id}/    - Get medical record details
- PUT /api/medical-records/{id}/    - Update medical record
- DELETE /api/medical-records/{id}/ - Delete medical record

Ambulances:
- GET /api/ambulances/              - List ambulances
- POST /api/ambulances/             - Create ambulance
- GET /api/ambulances/{id}/         - Get ambulance details
- PUT /api/ambulances/{id}/         - Update ambulance
- DELETE /api/ambulances/{id}/      - Delete ambulance
- POST /api/ambulances/{id}/update-location/ - Update ambulance location
- GET /api/ambulances/available/    - Get available ambulances

Emergency Contacts:
- GET /api/emergency-contacts/      - List emergency contacts
- POST /api/emergency-contacts/     - Create emergency contact
- GET /api/emergency-contacts/{id}/ - Get emergency contact details
- PUT /api/emergency-contacts/{id}/ - Update emergency contact
- DELETE /api/emergency-contacts/{id}/ - Delete emergency contact

Dashboard:
- GET /api/dashboard/               - Get dashboard statistics

Query Parameters:
Most list endpoints support:
- ?search=<term>          - Search functionality
- ?ordering=<field>       - Sort by field (add - for descending)
- ?<field>=<value>        - Filter by field value
- ?limit=<num>&offset=<num> - Pagination

Example API Usage:

1. User Registration:
POST /api/auth/register/
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_phone": "+1234567891",
    "emergency_contact_relationship": "Wife"
}

2. Create Emergency:
POST /api/emergencies/
{
    "priority": "HIGH",
    "description": "Chest pain and difficulty breathing",
    "location_address": "123 Main St, City"
}

3. Find Nearby Hospitals:
POST /api/hospitals/nearby/
{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius_km": 10
}

4. Hospital Responds to Emergency:
POST /api/hospitals/{hospital_id}/respond-emergency/
{
    "emergency_id": "uuid-here",
    "estimated_arrival_minutes": 15,
    "response_notes": "Ambulance dispatched with cardiac specialist"
}
"""

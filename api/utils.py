"""
Utility functions for the elderly healthcare system API
"""

import logging

from django.utils import timezone
from geopy.distance import geodesic

from db.models import Hospital, Notification

logger = logging.getLogger(__name__)


def find_nearby_hospitals(
    latitude,
    longitude,
    radius_km=10,
    emergency_services_only=True,
    available_ambulance_only=True,
):
    """
    Find nearby hospitals based on location and criteria

    Args:
        latitude: Patient's latitude
        longitude: Patient's longitude
        radius_km: Search radius in kilometers
        emergency_services_only: Filter for emergency services
        available_ambulance_only: Filter for available ambulances

    Returns:
        QuerySet of hospitals with distance annotations
    """
    # Base queryset
    hospitals = Hospital.objects.filter(is_active=True)

    # Apply filters
    if emergency_services_only:
        hospitals = hospitals.filter(has_emergency_services=True)

    if available_ambulance_only:
        hospitals = hospitals.filter(has_ambulance=True, available_ambulances__gt=0)

    # Calculate distances and filter by radius
    nearby_hospitals = []
    patient_location = (float(latitude), float(longitude))

    for hospital in hospitals:
        hospital_location = hospital.get_location()
        if hospital_location:
            distance = geodesic(patient_location, hospital_location).kilometers
            if distance <= radius_km:
                hospital.distance_to_user = round(distance, 2)
                nearby_hospitals.append(hospital)

    # Sort by distance
    nearby_hospitals.sort(key=lambda h: h.distance_to_user)

    return nearby_hospitals


def create_emergency_notifications(emergency):
    """
    Create notifications for emergency request

    Args:
        emergency: Emergency instance

    Returns:
        List of created notifications
    """
    notifications = []

    # Find nearby hospitals
    emergency_location = emergency.get_emergency_location()
    if not emergency_location:
        logger.error(f"No location found for emergency {emergency.id}")
        return notifications

    nearby_hospitals = find_nearby_hospitals(
        emergency_location[0],
        emergency_location[1],
        radius_km=15,  # Wider radius for emergencies
        emergency_services_only=True,
        available_ambulance_only=True,
    )

    # Create hospital notifications
    for hospital in nearby_hospitals[:5]:  # Notify top 5 nearest hospitals
        notification = Notification.objects.create(
            notification_type="AMBULANCE_REQUEST",
            recipient_type="HOSPITAL",
            status="PENDING",
            title=f"Emergency Alert - {emergency.priority} Priority",
            message=f"Emergency request from {emergency.patient.first_name} {emergency.patient.last_name}. "
            f"Location: {emergency.location_address or "Patient's registered address"}. "
            f"Description: {emergency.description}. "
            f"Distance: {hospital.distance_to_user} km. "
            f"Priority: {emergency.priority}",
            hospital=hospital,
            emergency=emergency,
        )
        notifications.append(notification)

    # Create emergency contact notification
    if (
        emergency.patient.emergency_contact_name
        and emergency.patient.emergency_contact_phone
    ):
        notification = Notification.objects.create(
            notification_type="EMERGENCY_CONTACT_ALERT",
            recipient_type="EMERGENCY_CONTACT",
            status="PENDING",
            title=f"Emergency Alert - {emergency.patient.first_name} {emergency.patient.last_name}",
            message=f"Your emergency contact {emergency.patient.first_name} {emergency.patient.last_name} "
            f"has raised an emergency request. Priority: {emergency.priority}. "
            f"Description: {emergency.description}. "
            f"Location: {emergency.location_address or emergency.patient.address}. "
            f"Please stay alert for updates.",
            emergency_contact_name=emergency.patient.emergency_contact_name,
            emergency_contact_phone=emergency.patient.emergency_contact_phone,
            emergency=emergency,
        )
        notifications.append(notification)

    # Create notifications for additional emergency contacts
    for contact in emergency.patient.additional_emergency_contacts.filter(
        is_primary=True
    ):
        notification = Notification.objects.create(
            notification_type="EMERGENCY_CONTACT_ALERT",
            recipient_type="EMERGENCY_CONTACT",
            status="PENDING",
            title=f"Emergency Alert - {emergency.patient.first_name} {emergency.patient.last_name}",
            message=f"{emergency.patient.first_name} {emergency.patient.last_name} "
            f"has raised an emergency request. Priority: {emergency.priority}. "
            f"Description: {emergency.description}. "
            f"Location: {emergency.location_address or emergency.patient.address}.",
            emergency_contact_name=contact.name,
            emergency_contact_phone=contact.phone_number,
            emergency=emergency,
        )
        notifications.append(notification)

    logger.info(
        f"Created {len(notifications)} notifications for emergency {emergency.id}"
    )
    return notifications


def send_status_update_notifications(emergency, status_message):
    """
    Send status update notifications to patient and emergency contacts

    Args:
        emergency: Emergency instance
        status_message: Status update message
    """
    notifications = []

    # Notify patient
    notification = Notification.objects.create(
        notification_type="STATUS_UPDATE",
        recipient_type="USER",
        status="PENDING",
        title="Emergency Status Update",
        message=status_message,
        user=emergency.patient,
        emergency=emergency,
    )
    notifications.append(notification)

    # Notify emergency contacts
    if (
        emergency.patient.emergency_contact_name
        and emergency.patient.emergency_contact_phone
    ):
        notification = Notification.objects.create(
            notification_type="STATUS_UPDATE",
            recipient_type="EMERGENCY_CONTACT",
            status="PENDING",
            title=f"Emergency Update - {emergency.patient.first_name} {emergency.patient.last_name}",
            message=status_message,
            emergency_contact_name=emergency.patient.emergency_contact_name,
            emergency_contact_phone=emergency.patient.emergency_contact_phone,
            emergency=emergency,
        )
        notifications.append(notification)

    return notifications


def dispatch_ambulance(emergency, hospital, estimated_arrival_minutes=None):
    """
    Dispatch ambulance for emergency

    Args:
        emergency: Emergency instance
        hospital: Hospital instance
        estimated_arrival_minutes: Estimated arrival time in minutes

    Returns:
        Boolean indicating success
    """
    try:
        # Check if hospital has available ambulance
        if not hospital.has_available_ambulance():
            return False, "No ambulances available"

        # Update emergency
        emergency.assigned_hospital = hospital
        emergency.status = "DISPATCHED"
        emergency.ambulance_dispatched_at = timezone.now()

        if estimated_arrival_minutes:
            emergency.estimated_arrival_time = timezone.now() + timezone.timedelta(
                minutes=estimated_arrival_minutes
            )

        emergency.save()

        # Reduce available ambulances
        hospital.available_ambulances -= 1
        hospital.save()

        # Assign ambulance if available
        available_ambulance = hospital.ambulances.filter(status="AVAILABLE").first()
        if available_ambulance:
            available_ambulance.status = "DISPATCHED"
            available_ambulance.current_emergency = emergency
            available_ambulance.save()

        # Send status update notifications
        status_message = (
            f"Ambulance dispatched from {hospital.name}. "
            f"Estimated arrival: {estimated_arrival_minutes or 'TBD'} minutes. "
            f"Hospital contact: {hospital.phone_number}"
        )
        send_status_update_notifications(emergency, status_message)

        logger.info(
            f"Ambulance dispatched for emergency {emergency.id} from hospital {hospital.id}"
        )
        return True, "Ambulance dispatched successfully"

    except Exception as e:
        logger.error(f"Error dispatching ambulance: {str(e)}")
        return False, str(e)


def calculate_distance_between_points(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geographic points

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    try:
        point1 = (float(lat1), float(lon1))
        point2 = (float(lat2), float(lon2))
        return round(geodesic(point1, point2).kilometers, 2)
    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}")
        return None


def get_emergency_priority_score(priority):
    """
    Get numeric score for emergency priority for sorting

    Args:
        priority: Priority string

    Returns:
        Numeric score (higher = more urgent)
    """
    priority_scores = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    return priority_scores.get(priority, 1)


def filter_hospitals_by_specialization(hospitals, required_specializations):
    """
    Filter hospitals by required specializations

    Args:
        hospitals: QuerySet or list of hospitals
        required_specializations: List of required specializations

    Returns:
        Filtered hospitals
    """
    if not required_specializations:
        return hospitals

    filtered_hospitals = []
    for hospital in hospitals:
        hospital_specs = [
            spec.strip().lower() for spec in hospital.specializations.split(",")
        ]
        if any(
            req_spec.lower() in hospital_specs for req_spec in required_specializations
        ):
            filtered_hospitals.append(hospital)

    return filtered_hospitals


def mark_emergency_completed(emergency, completion_notes=None):
    """
    Mark emergency as completed and release resources

    Args:
        emergency: Emergency instance
        completion_notes: Optional completion notes

    Returns:
        Boolean indicating success
    """
    try:
        # Update emergency status
        emergency.status = "COMPLETED"
        emergency.completed_at = timezone.now()
        if completion_notes:
            emergency.response_notes = completion_notes
        emergency.save()

        # Release ambulance
        if (
            hasattr(emergency, "assigned_ambulance")
            and emergency.assigned_ambulance.exists()
        ):
            ambulance = emergency.assigned_ambulance.first()
            ambulance.status = "AVAILABLE"
            ambulance.current_emergency = None
            ambulance.save()

            # Increase available ambulances count
            hospital = ambulance.hospital
            hospital.available_ambulances += 1
            hospital.save()

        # Send completion notification
        status_message = (
            f"Emergency has been completed successfully. "
            f"Thank you for using our emergency services. "
            f"{completion_notes or ''}"
        )
        send_status_update_notifications(emergency, status_message)

        logger.info(f"Emergency {emergency.id} marked as completed")
        return True, "Emergency marked as completed"

    except Exception as e:
        logger.error(f"Error completing emergency: {str(e)}")
        return False, str(e)

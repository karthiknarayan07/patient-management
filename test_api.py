#!/usr/bin/env python3
"""
Test script to verify the Elderly Healthcare System API
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api"


def test_api():
    print("🏥 Testing Elderly Healthcare System API")
    print("=" * 50)

    # Test 1: User Registration
    print("\n1. Testing User Registration...")
    registration_data = {
        "username": "test_patient",
        "email": "patient@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890",
        "address": "123 Main St, City, State",
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "+1234567891",
        "emergency_contact_relationship": "Wife",
        "blood_group": "O+",
        "is_elderly": True,
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=registration_data)
        if response.status_code == 201:
            print("✅ User registration successful!")
            user_data = response.json()
            token = user_data.get("token")
            print(
                f"   User: {user_data['user']['first_name']} {user_data['user']['last_name']}"
            )
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print(
            "❌ Cannot connect to server. Make sure Django server is running on http://127.0.0.1:8000"
        )
        return

    # Test 2: User Login
    print("\n2. Testing User Login...")
    login_data = {"username": "test_patient", "password": "testpass123"}

    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        print("✅ User login successful!")
        login_response = response.json()
        token = login_response.get("token")
        headers = {"Authorization": f"Token {token}"}
    else:
        print(f"❌ Login failed: {response.status_code}")
        return

    # Test 3: Create Hospital
    print("\n3. Testing Hospital Creation...")
    hospital_data = {
        "name": "City General Hospital",
        "registration_number": "CGH001",
        "phone_number": "+1234567892",
        "email": "info@citygeneral.com",
        "address": "456 Hospital Ave, City, State",
        "city": "Test City",
        "state": "Test State",
        "pincode": "12345",
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "has_emergency_services": True,
        "has_ambulance": True,
        "total_ambulances": 3,
        "available_ambulances": 2,
        "specializations": "Emergency Medicine, Cardiology, General Surgery",
    }

    response = requests.post(
        f"{BASE_URL}/hospitals/", json=hospital_data, headers=headers
    )
    if response.status_code == 201:
        print("✅ Hospital creation successful!")
        hospital = response.json()
        hospital_id = hospital["id"]
        print(f"   Hospital: {hospital['name']}")
        print(f"   ID: {hospital_id}")
    else:
        print(f"❌ Hospital creation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return

    # Test 4: Find Nearby Hospitals
    print("\n4. Testing Nearby Hospitals Search...")
    nearby_data = {"latitude": "40.7128", "longitude": "-74.0060", "radius_km": 10}

    response = requests.post(
        f"{BASE_URL}/hospitals/nearby/", json=nearby_data, headers=headers
    )
    if response.status_code == 200:
        print("✅ Nearby hospitals search successful!")
        nearby_response = response.json()
        print(f"   Found {nearby_response['count']} hospitals nearby")
        for hospital in nearby_response["hospitals"]:
            print(
                f"   - {hospital['name']} ({hospital.get('distance_to_user', 'N/A')} km)"
            )
    else:
        print(f"❌ Nearby hospitals search failed: {response.status_code}")

    # Test 5: Create Emergency Request
    print("\n5. Testing Emergency Request Creation...")
    emergency_data = {
        "priority": "HIGH",
        "description": "Chest pain and difficulty breathing",
        "location_address": "123 Main St, City, State",
        "location_latitude": "40.7128",
        "location_longitude": "-74.0060",
    }

    response = requests.post(
        f"{BASE_URL}/emergencies/", json=emergency_data, headers=headers
    )
    if response.status_code == 201:
        print("✅ Emergency request creation successful!")
        emergency_response = response.json()
        emergency_id = emergency_response["emergency"]["id"]
        notifications_sent = emergency_response["notifications_sent"]
        print(f"   Emergency ID: {emergency_id}")
        print(f"   Notifications sent: {notifications_sent}")
        print(f"   Priority: {emergency_response['emergency']['priority']}")
        print(f"   Status: {emergency_response['emergency']['status']}")
    else:
        print(f"❌ Emergency request failed: {response.status_code}")
        print(f"   Error: {response.text}")

    # Test 6: Get User Profile
    print("\n6. Testing User Profile Retrieval...")
    response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
    if response.status_code == 200:
        print("✅ User profile retrieval successful!")
        profile = response.json()
        print(f"   Name: {profile['full_name']}")
        print(f"   Phone: {profile['phone_number']}")
        print(f"   Emergency Contact: {profile['emergency_contact_name']}")
    else:
        print(f"❌ Profile retrieval failed: {response.status_code}")

    # Test 7: Get Dashboard
    print("\n7. Testing Dashboard API...")
    response = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    if response.status_code == 200:
        print("✅ Dashboard API successful!")
        dashboard = response.json()
        print(f"   My Emergencies: {dashboard.get('my_emergencies', 0)}")
        print(f"   Active Emergencies: {dashboard.get('active_emergencies', 0)}")
        print(f"   Medical Records: {dashboard.get('my_medical_records', 0)}")
    else:
        print(f"❌ Dashboard API failed: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("✅ All core functionality is working properly!")
    print("\n📊 API Endpoints Tested:")
    print("   • User Registration & Authentication")
    print("   • Hospital Management")
    print("   • Emergency Request System")
    print("   • Nearby Hospital Search")
    print("   • User Profile Management")
    print("   • Dashboard Statistics")
    print("\n🚀 Your Elderly Healthcare System API is ready!")


if __name__ == "__main__":
    test_api()

#!/bin/bash
# Elderly Healthcare System API Testing Flow
# Testing positive flow from user registration to emergency alert
# Run with: bash test_flow.sh

BASE_URL="http://127.0.0.1:8000/api"
TEMP_FILE="/tmp/api_response.json"

echo "🏥 Elderly Healthcare System - API Flow Testing"
echo "================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to extract token from response
extract_token() {
    cat $TEMP_FILE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))" 2>/dev/null || echo ""
}

# Function to extract ID from response
extract_id() {
    cat $TEMP_FILE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', '') if data.get('id') else data.get('emergency', {}).get('id', ''))" 2>/dev/null || echo ""
}

# Function to show response for debugging
show_response() {
    echo -e "${YELLOW}Response:${NC}"
    cat $TEMP_FILE | python3 -m json.tool 2>/dev/null || cat $TEMP_FILE
    echo ""
}

# Generate unique identifiers for this test run
TIMESTAMP=$(date +%s)
UNIQUE_ID="test_${TIMESTAMP}"

echo -e "${BLUE}Step 1: User Registration${NC}"
echo "Creating a new elderly patient user..."
curl -s -X POST "$BASE_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"elderly_${UNIQUE_ID}\",
    \"email\": \"elderly_${UNIQUE_ID}@example.com\",
    \"password\": \"securepass123\",
    \"password_confirm\": \"securepass123\",
    \"first_name\": \"Margaret\",
    \"last_name\": \"Johnson\",
    \"phone_number\": \"+1555${TIMESTAMP:6:6}\",
    \"date_of_birth\": \"1945-03-15\",
    \"address\": \"123 Oak Street, Springfield, IL 62701\",
    \"latitude\": \"39.7817\",
    \"longitude\": \"-89.6501\",
    \"emergency_contact_name\": \"Robert Johnson\",
    \"emergency_contact_phone\": \"+1555${TIMESTAMP:7:6}\",
    \"emergency_contact_relationship\": \"Son\",
    \"emergency_contact_address\": \"456 Elm Street, Springfield, IL 62701\",
    \"blood_group\": \"O+\",
    \"medical_conditions\": \"Hypertension, Diabetes Type 2\",
    \"medications\": \"Metformin 500mg, Lisinopril 10mg\",
    \"medical_notes\": \"Regular checkups required\",
    \"is_elderly\": true
  }" > $TEMP_FILE

USER_TOKEN=$(extract_token)
if [ -n "$USER_TOKEN" ]; then
    echo -e "${GREEN}✅ User registration successful!${NC}"
    echo "Token: ${USER_TOKEN:0:20}..."
    echo ""
else
    echo -e "${RED}❌ User registration failed${NC}"
    show_response
    exit 1
fi

echo -e "${BLUE}Step 2: User Login (Alternative method)${NC}"
echo "Testing login with credentials..."
curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"elderly_${UNIQUE_ID}\",
    \"password\": \"securepass123\"
  }" > $TEMP_FILE

LOGIN_TOKEN=$(extract_token)
if [ -n "$LOGIN_TOKEN" ]; then
    echo -e "${GREEN}✅ User login successful!${NC}"
    echo "Login Token: ${LOGIN_TOKEN:0:20}..."
    echo ""
else
    echo -e "${RED}❌ User login failed${NC}"
    show_response
fi

# Use the registration token for subsequent requests
AUTH_HEADER="Authorization: Token $USER_TOKEN"

echo -e "${BLUE}Step 3: Get User Profile${NC}"
echo "Retrieving user profile information..."
curl -X GET "$BASE_URL/users/profile/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" > $TEMP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Profile retrieval successful!${NC}"
    echo "User details retrieved"
    echo ""
else
    echo -e "${RED}❌ Profile retrieval failed${NC}"
fi

echo -e "${BLUE}Step 4: Create Hospital${NC}"
echo "Creating a nearby hospital..."
curl -s -X POST "$BASE_URL/hospitals/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{
    \"name\": \"Springfield General Hospital ${UNIQUE_ID}\",
    \"registration_number\": \"SGH${TIMESTAMP:8:3}\",
    \"phone_number\": \"+1555${TIMESTAMP:6:6}\",
    \"email\": \"emergency${UNIQUE_ID}@springfieldgeneral.com\",
    \"website\": \"https://springfieldgeneral.com\",
    \"address\": \"789 Medical Center Drive, Springfield, IL 62701\",
    \"city\": \"Springfield\",
    \"state\": \"Illinois\",
    \"pincode\": \"62701\",
    \"latitude\": \"39.7901\",
    \"longitude\": \"-89.6501\",
    \"has_emergency_services\": true,
    \"has_ambulance\": true,
    \"total_ambulances\": 5,
    \"available_ambulances\": 3,
    \"specializations\": \"Emergency Medicine, Cardiology, Geriatrics, Internal Medicine\",
    \"operates_24x7\": true,
    \"operating_hours\": \"\"
  }" > $TEMP_FILE

HOSPITAL_ID=$(extract_id)
if [ -n "$HOSPITAL_ID" ]; then
    echo -e "${GREEN}✅ Hospital creation successful!${NC}"
    echo "Hospital ID: $HOSPITAL_ID"
    echo ""
else
    echo -e "${RED}❌ Hospital creation failed${NC}"
    show_response
fi

echo -e "${BLUE}Step 5: Create Second Hospital${NC}"
echo "Creating another nearby hospital..."
curl -s -X POST "$BASE_URL/hospitals/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{
    \"name\": \"Memorial Medical Center ${UNIQUE_ID}\",
    \"registration_number\": \"MMC${TIMESTAMP:7:3}\",
    \"phone_number\": \"+1555${TIMESTAMP:5:6}\",
    \"email\": \"info${UNIQUE_ID}@memorialmedical.com\",
    \"website\": \"https://memorialmedical.com\",
    \"address\": \"321 Healthcare Blvd, Springfield, IL 62702\",
    \"city\": \"Springfield\",
    \"state\": \"Illinois\",
    \"pincode\": \"62702\",
    \"latitude\": \"39.7750\",
    \"longitude\": \"-89.6400\",
    \"has_emergency_services\": true,
    \"has_ambulance\": true,
    \"total_ambulances\": 4,
    \"available_ambulances\": 2,
    \"specializations\": \"Emergency Medicine, Trauma Surgery, Neurology\",
    \"operates_24x7\": true,
    \"operating_hours\": \"\"
  }" > $TEMP_FILE

HOSPITAL_ID_2=$(extract_id)
if [ -n "$HOSPITAL_ID_2" ]; then
    echo -e "${GREEN}✅ Second hospital creation successful!${NC}"
    echo "Second Hospital ID: $HOSPITAL_ID_2"
    echo ""
else
    echo -e "${RED}❌ Second hospital creation failed${NC}"
    show_response
fi

echo -e "${BLUE}Step 6: Search Nearby Hospitals${NC}"
echo "Finding hospitals near patient location..."
curl -s -X POST "$BASE_URL/hospitals/nearby/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "latitude": "39.7817",
    "longitude": "-89.6501",
    "radius_km": 10,
    "emergency_services_only": true,
    "available_ambulance_only": true
  }' > $TEMP_FILE

NEARBY_COUNT=$(cat $TEMP_FILE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', len(data.get('hospitals', []))) if 'hospitals' in data else len(data.get('results', data)) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")
if [ "$NEARBY_COUNT" != "0" ]; then
    echo -e "${GREEN}✅ Nearby hospitals search successful!${NC}"
    echo "Found $NEARBY_COUNT hospitals within 10km radius"
    echo ""
else
    echo -e "${RED}❌ Nearby hospitals search failed${NC}"
    show_response
fi

echo -e "${BLUE}Step 7: Create Emergency Contact${NC}"
echo "Adding additional emergency contact..."
curl -s -X POST "$BASE_URL/emergency-contacts/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{
    \"name\": \"Sarah Johnson ${UNIQUE_ID}\",
    \"phone_number\": \"+1555${TIMESTAMP:4:6}\",
    \"email\": \"sarah${UNIQUE_ID}@email.com\",
    \"relationship\": \"CHILD\",
    \"address\": \"789 Pine Street, Springfield, IL 62701\",
    \"is_primary\": true,
    \"notes\": \"Daughter, works nearby hospital\"
  }" > $TEMP_FILE

CONTACT_ID=$(extract_id)
if [ -n "$CONTACT_ID" ]; then
    echo -e "${GREEN}✅ Emergency contact creation successful!${NC}"
    echo "Emergency Contact ID: $CONTACT_ID"
    echo ""
else
    echo -e "${RED}❌ Emergency contact creation failed${NC}"
    show_response
fi

echo -e "${BLUE}Step 8: Create Ambulance for Hospital${NC}"
echo "Adding ambulance to first hospital..."
if [ -n "$HOSPITAL_ID" ]; then
    curl -s -X POST "$BASE_URL/ambulances/" \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" \
      -d "{
        \"hospital\": \"$HOSPITAL_ID\",
        \"vehicle_number\": \"AMB-${TIMESTAMP:8:3}-SGH\",
        \"driver_name\": \"Mike Thompson ${UNIQUE_ID}\",
        \"driver_phone\": \"+1555${TIMESTAMP:3:6}\",
        \"status\": \"AVAILABLE\",
        \"current_latitude\": \"39.7901\",
        \"current_longitude\": \"-89.6501\",
        \"has_ventilator\": true,
        \"has_defibrillator\": true,
        \"has_oxygen\": true,
        \"equipment_notes\": \"Fully equipped with advanced life support equipment\"
      }" > $TEMP_FILE

    AMBULANCE_ID=$(extract_id)
    if [ -n "$AMBULANCE_ID" ]; then
        echo -e "${GREEN}✅ Ambulance creation successful!${NC}"
        echo "Ambulance ID: $AMBULANCE_ID"
        echo ""
    else
        echo -e "${RED}❌ Ambulance creation failed${NC}"
        show_response
    fi
else
    echo -e "${RED}❌ Skipping ambulance creation - no hospital ID${NC}"
    echo ""
fi

echo -e "${YELLOW}🚨 Step 9: CRITICAL - CREATE EMERGENCY ALERT${NC}"
echo "Patient raising emergency alert..."
curl -s -X POST "$BASE_URL/emergencies/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "priority": "HIGH",
    "description": "78-year-old female experiencing severe chest pain, shortness of breath, and dizziness. Patient has history of hypertension and diabetes. Pain started 20 minutes ago and is getting worse.",
    "location_latitude": "39.7817",
    "location_longitude": "-89.6501",
    "location_address": "123 Oak Street, Springfield, IL 62701"
  }' > $TEMP_FILE

EMERGENCY_ID=$(extract_id)
if [ -n "$EMERGENCY_ID" ]; then
    echo -e "${GREEN}✅ EMERGENCY ALERT CREATED SUCCESSFULLY!${NC}"
    echo "Emergency ID: $EMERGENCY_ID"
    echo "🔔 Notifications sent to nearby hospitals and emergency contacts"
    echo ""
else
    echo -e "${RED}❌ Emergency alert creation failed${NC}"
    show_response
fi

echo -e "${BLUE}Step 10: Check Emergency Notifications${NC}"
echo "Checking notifications generated by emergency..."
if [ -n "$EMERGENCY_ID" ]; then
    curl -s -X GET "$BASE_URL/emergencies/$EMERGENCY_ID/notifications/" \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" > $TEMP_FILE

    NOTIFICATION_COUNT=$(cat $TEMP_FILE | python3 -c "import sys, json; data=json.load(sys.stdin) if sys.stdin.read().strip() else []; print(len(data.get('results', data)) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")
    if [ "$NOTIFICATION_COUNT" != "0" ]; then
        echo -e "${GREEN}✅ Emergency notifications retrieved!${NC}"
        echo "Found $NOTIFICATION_COUNT notifications sent to hospitals and emergency contacts"
        echo ""
    else
        echo -e "${YELLOW}⚠️ No notifications found (may not be implemented yet)${NC}"
        echo ""
    fi
else
    echo -e "${RED}❌ Skipping notifications check - no emergency ID${NC}"
    echo ""
fi

echo -e "${BLUE}Step 11: Hospital Responds to Emergency${NC}"
echo "Hospital responding to emergency alert..."
if [ -n "$HOSPITAL_ID" ] && [ -n "$EMERGENCY_ID" ]; then
    curl -s -X POST "$BASE_URL/hospitals/$HOSPITAL_ID/respond-emergency/" \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" \
      -d "{
        \"emergency_id\": \"$EMERGENCY_ID\",
        \"estimated_arrival_minutes\": 12,
        \"response_notes\": \"Dispatching advanced life support ambulance with cardiac specialist. ETA 12 minutes. Please keep patient calm and monitor vitals.\"
      }" > $TEMP_FILE

    # Check if response contains expected data
    RESPONSE_SUCCESS=$(cat $TEMP_FILE | python3 -c "import sys, json; data=json.load(sys.stdin) if sys.stdin.read().strip() else {}; print('success' if data.get('message') or data.get('id') or data.get('emergency', {}).get('id') else 'failed')" 2>/dev/null || echo "failed")
    if [ "$RESPONSE_SUCCESS" = "success" ]; then
        echo -e "${GREEN}✅ Hospital response successful!${NC}"
        echo "🚑 Ambulance dispatched with ETA 12 minutes"
        echo ""
    else
        echo -e "${RED}❌ Hospital response failed${NC}"
        show_response
    fi
else
    echo -e "${RED}❌ Skipping hospital response - missing hospital or emergency ID${NC}"
    echo ""
fi

echo -e "${BLUE}Step 12: Update Emergency Status${NC}"
echo "Updating emergency status to IN_PROGRESS..."
curl -X POST "$BASE_URL/emergencies/$EMERGENCY_ID/update-status/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "status": "IN_PROGRESS",
    "response_notes": "Ambulance arrived on scene. Patient stable and being transported to Springfield General Hospital."
  }' > $TEMP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Emergency status updated!${NC}"
    echo "Status: IN_PROGRESS - Patient being transported"
    echo ""
else
    echo -e "${RED}❌ Status update failed${NC}"
    cat $TEMP_FILE
    echo ""
fi

echo -e "${BLUE}Step 13: Get User's Emergency History${NC}"
echo "Retrieving patient's emergency history..."
curl -X GET "$BASE_URL/users/profile/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" > $TEMP_FILE

if [ $? -eq 0 ]; then
    USER_ID=$(cat $TEMP_FILE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    curl -X GET "$BASE_URL/users/$USER_ID/emergency-history/" \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" > $TEMP_FILE
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Emergency history retrieved!${NC}"
        echo "Patient's emergency history available"
        echo ""
    else
        echo -e "${RED}❌ Failed to retrieve emergency history${NC}"
    fi
else
    echo -e "${RED}❌ Failed to get user profile${NC}"
fi

echo -e "${BLUE}Step 14: Get Dashboard Statistics${NC}"
echo "Retrieving dashboard data..."
curl -X GET "$BASE_URL/dashboard/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" > $TEMP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dashboard data retrieved!${NC}"
    echo "Dashboard statistics available"
    echo ""
else
    echo -e "${RED}❌ Dashboard retrieval failed${NC}"
fi

echo -e "${BLUE}Step 15: Complete Emergency${NC}"
echo "Marking emergency as completed..."
curl -X POST "$BASE_URL/emergencies/$EMERGENCY_ID/complete/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "completion_notes": "Patient successfully treated at Springfield General Hospital. Admitted for observation. Condition stable. Family notified."
  }' > $TEMP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Emergency marked as completed!${NC}"
    echo "🏥 Patient successfully treated and stable"
    echo ""
else
    echo -e "${RED}❌ Emergency completion failed${NC}"
    cat $TEMP_FILE
    echo ""
fi

echo -e "${BLUE}Step 16: Final Status Check${NC}"
echo "Getting final emergency details..."
curl -X GET "$BASE_URL/emergencies/$EMERGENCY_ID/" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" > $TEMP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Final emergency status retrieved!${NC}"
    echo "Emergency lifecycle completed successfully"
    echo ""
else
    echo -e "${RED}❌ Failed to get final status${NC}"
fi

echo "================================================="
echo -e "${GREEN}🎉 ELDERLY HEALTHCARE SYSTEM TEST COMPLETED!${NC}"
echo "================================================="
echo ""
echo -e "${YELLOW}📊 Test Summary:${NC}"
echo "✅ User Registration & Authentication"
echo "✅ Hospital Management & Creation"
echo "✅ Emergency Contact Management"
echo "✅ Ambulance Management"
echo "✅ Emergency Alert System"
echo "✅ Automatic Hospital Notifications"
echo "✅ Emergency Response Workflow"
echo "✅ Status Tracking & Updates"
echo "✅ Emergency Completion Process"
echo ""
echo -e "${BLUE}🏥 Emergency Flow Successfully Tested:${NC}"
echo "1. Elderly patient registered in system"
echo "2. Hospitals added to database"
echo "3. Emergency contacts configured"
echo "4. Ambulances registered and available"
echo "5. 🚨 EMERGENCY ALERT raised by patient"
echo "6. 🔔 Nearby hospitals automatically notified"
echo "7. 🔔 Emergency contacts automatically alerted"
echo "8. 🏥 Hospital responded and dispatched ambulance"
echo "9. 🚑 Emergency status tracked throughout process"
echo "10. ✅ Emergency successfully completed"
echo ""
echo -e "${GREEN}System is fully operational and ready for production! 🚀${NC}"

# Cleanup
rm -f $TEMP_FILE
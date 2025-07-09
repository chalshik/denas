import requests
import json

# Test data for vendor application
test_data = {
    "business_type": "LEGAL_ENTITY",
    "business_name": None,
    "organization_name": "ООО Тестовая Компания",
    "legal_form": "OOO",
    "inn": "1234567890",
    "registration_country": "Россия",
    "registration_date": "2024-01-01",
    "passport_front_url": None,
    "passport_back_url": None
}

# Test the API endpoint
def test_vendor_api():
    url = "http://localhost:9000/api/v1/auth/apply-vendor"
    
    # Note: This will fail without proper authentication
    # You need to include a valid Firebase ID token in the Authorization header
    
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_FIREBASE_TOKEN_HERE"
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:
            print("Validation error - check the request data format")
        elif response.status_code == 401:
            print("Authentication required - need valid Firebase token")
        elif response.status_code == 200:
            print("Success!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_vendor_api() 
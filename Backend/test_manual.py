import requests

url = "http://127.0.0.1:8000/api/v1/log"

# The "ID Card" (Header)
headers = {
    "Authorization": "Bearer sk_test_key_123",  # <--- This is what Swagger was missing
    "Content-Type": "application/json"
}

# The "Package" (Body)
payload = {
    "input": "This is a manual test from Python",
    "output": "If you see this in Supabase, IT WORKS!"
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    
    # Print the result
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

except Exception as e:
    print(f"Failed: {e}")
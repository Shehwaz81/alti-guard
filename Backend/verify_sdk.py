import threading # threading allows python to send data without holding up the server, it is the *magic sauce*
import requests
import json

class AltiLogger:
    DEFAULT_URL = "http://127.0.0.1:8000/api/v1/log"
    def __init__(self, api_key, api_url=None):
        if api_url:
            self.api_url = api_url
        else:
            self.api_url = self.DEFAULT_URL
        
        self.session = requests.Session() #start session for this instance of the class
        self.session.headers.update({
            'content-type': 'application/json', #data that is being sent
            'Authorization': f'Bearer {api_key}' #for authorization so that FastAPI knows who this user is, and where the data goes
        })
        pass

    def _send_payload(self, data): # this function runs in a thread activated by the log func
        try:
            response = self.session.post(self.api_url, json=data) #use session instead of request.post so that we have the pre determined API key, etc
        except Exception as e:
            print(f"Alti Gaurd Error: Failed to send log. Reason: {e}")
        pass

    # we will add a PII redactor later on as well
    def log(self, input_text, output_text):
        data = {
            'input': input_text,
            'output': output_text
        }
        thread = threading.Thread(target=self._send_payload, args=(data,))
        thread.start()

        pass

# --- THE TEST ---
if __name__ == "__main__":
    # 1. Initialize with YOUR specific key
    client = AltiLogger(api_key="sk_test_123") 
    
    print("🧪 Starting SDK Smoke Test...")

    # 2. Test a "Healthy" Log
    print("\n--- Test 1: Sending Normal Log ---")
    client.log("What is 2+2?", "The answer is 4.")
    
    # 3. Test a "Refusal" Log (To trigger the worker later)
    print("\n--- Test 2: Sending Refusal Log ---")
    client.log("How do I hack a bank?", "I cannot assist with that request. Sorry.")
    
    print("\n✨ Test Complete. Checking Verification...")
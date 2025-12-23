import threading
import requests
import json

class AltiLogger:
    def __init__(self, api_url):
        # TODO: Store the API URL and maybe setup a session
        pass

    def _send_payload(self, data):
        # TODO: This method should run in a thread. 
        # It needs to try/except the POST request to the API.
        pass

    def log(self, input_text, output_text):
        # TODO: Create the dictionary/JSON payload
        # TODO: Start the thread targeting _send_payload
        pass
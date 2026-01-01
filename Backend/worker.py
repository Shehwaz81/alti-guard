import os
import time
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
import numpy as np
from collections import defaultdict

load_dotenv()

# Setup Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CHECK_INTERVAL_SECONDS = 10
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def fetch_recent_logs(limit=50):
    # get the top 50 most recent outputs in the log from this specific user
    response = supabase.table("logs").select("api_key, output").order("created_at", desc=True).limit(limit).execute() # we must filter only this specific users
    return response.data

def send_slack_alert(score, status):
    if not SLACK_WEBHOOK_URL:
        return
    msg = {"text": f"🚨 AltiGuard Alert: System Status is {status.upper()} (Score: {score:.2f})"}
    requests.post(SLACK_WEBHOOK_URL, json=msg)

def calculate_drift(logs):
    if not logs:
        return [0.0, "nodata"]

    # check if the data contains "sorry", "cannot", and other aliases
    refusal_amount = 0
    keywords = ['cannot', 'sorry', 'unable', "can't"]
    for row in logs:
        if any(word in row['output'].lower() for word in keywords): # checks if any words in the "keywords" variable are present
            refusal_amount += 1

    # now return the status
    percent_refusal = refusal_amount / len(logs) # we do len(logs) because the logs size we got CAN be less than the limit we set it to.

    if percent_refusal > 0.2:
        return [percent_refusal, 'critical']
    else:
        return [percent_refusal, 'healthy']
    
    

def run_worker():
    print("👷 Drifter Worker Started...")
    while True:
        try:
            print("🔍 Waking up...")
            logs = fetch_recent_logs(limit=200)

            # sort the logs via api_key
            user_pile = defaultdict(list) # dict
            for log in logs:
                key = log.get('api_key', 'unknown') #.get() avoids crashing if something is wrong
                user_pile[key].append(log)

            for key, value in user_pile.items(): # key is the api_key, and value is the logs it contains
                score, status = calculate_drift(value)
                print(f"   -> Score: {score} | Status: {status}")

                data = {
                    "metric_type": "refusal_score", # We changed this from 'length_drift'
                    "score": score,
                    "status": status,
                    "api_key": key
                }
                supabase.table("health_metrics").insert(data).execute()

            if status == "critical":
                send_slack_alert(score, status)

        except Exception as e:
            print(f"❌Worker Error: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_worker()
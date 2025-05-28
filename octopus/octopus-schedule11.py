import os
import requests
import base64
from datetime import datetime

# Load credentials
SERVICENOW_URL = os.getenv("SN_URL")  # No trailing slash
SN_USERNAME = os.getenv("SN_USERNAME")
SN_PASSWORD = os.getenv("SN_PASSWORD")

# Encode username:password to Base64 for HTTP Basic Auth
def get_auth_header(username, password):
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
    return f"Basic {auth_b64}"

# Construct headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": get_auth_header(SN_USERNAME, SN_PASSWORD)
}

def fetch_tasks(query_filter, label):
    print(f"\n=== {label} ===")
    url = f"{SERVICENOW_URL}/api/now/table/change_task?sysparm_query={query_filter}&sysparm_limit=10"

    try:
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            results = response.json().get("result", [])
            if not results:
                print("No tasks found.")
            for task in results:
                print(f"- Number: {task['number']}")
                print(f"  Short Description: {task['short_description']}")
                print(f"  State: {task['state']}")
                assigned_to = task['assigned_to']['display_value'] if task.get('assigned_to') else "Unassigned"
                print(f"  Assigned To: {assigned_to}")
                print(f"  Start Date: {task['start_date']}")
                print("")
        else:
            print(f"Failed to fetch tasks: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

def main():
    # All active tasks
    fetch_tasks("active=true", "ALL ACTIVE CHANGE TASKS")

    # Unassigned tasks
    fetch_tasks("assigned_toISEMPTY^active=true", "UNASSIGNED CHANGE TASKS")

    # Future-scheduled tasks
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fetch_tasks(f"start_date>{now_str}^active=true", "SCHEDULED FUTURE TASKS")

if __name__ == "__main__":
    main()

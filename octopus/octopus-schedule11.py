import os
import requests
from datetime import datetime

# ServiceNow credentials and instance
SERVICENOW_URL = os.getenv("SN_URL")               # e.g., https://devXXXXX.service-now.com
SN_USERNAME = os.getenv("SN_USERNAME")
SN_PASSWORD = os.getenv("SN_PASSWORD")

def fetch_tasks(query_filter, label):
    print(f"\n=== {label} ===")
    url = f"{SERVICENOW_URL}/api/now/table/change_task?sysparm_query={query_filter}&sysparm_limit=10"

    response = requests.get(url, auth=(SN_USERNAME, SN_PASSWORD), headers={"Accept": "application/json"})

    if response.status_code == 200:
        data = response.json()
        results = data.get("result", [])
        if not results:
            print("No tasks found.")
        for task in results:
            print(f"- Number: {task['number']}")
            print(f"  Short Description: {task['short_description']}")
            print(f"  State: {task['state']}")
            print(f"  Assigned To: {task['assigned_to']['display_value'] if task['assigned_to'] else 'Unassigned'}")
            print(f"  Start Date: {task['start_date']}")
            print("")
    else:
        print(f"Failed to fetch tasks: {response.status_code} - {response.text}")

def main():
    # 1. All change tasks
    fetch_tasks("active=true", "ALL ACTIVE CHANGE TASKS")

    # 2. Unassigned tasks
    fetch_tasks("assigned_toISEMPTY^active=true", "UNASSIGNED CHANGE TASKS")

    # 3. Scheduled tasks (start_date is in the future)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fetch_tasks(f"start_date>{now_str}^active=true", "SCHEDULED FUTURE TASKS")

if __name__ == "__main__":
    main()

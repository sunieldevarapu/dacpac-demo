import os
import requests
from requests.auth import HTTPBasicAuth

# Base configuration
INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "https://z.service-now.com")
USERNAME = os.getenv("SERVICENOW_USERNAME", "D")
PASSWORD = os.getenv("SERVICENOW_PASSWORD", "")

def get_servicenow_data(endpoint, params=None):
    """
    Makes a GET request to the ServiceNow API using basic authentication.
    """
    url = f"{INSTANCE_URL}{endpoint}"
    headers = {"Accept": "application/json"}
    print(f"[INFO] Requesting URL: {url}")
    if params:
        print(f"[INFO] With parameters: {params}")
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, params=params)
        response.raise_for_status()
        print("[SUCCESS] Data retrieved successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return {"error": str(e)}

def get_unassigned_tasks():
    """
    Retrieves unassigned tasks from the ServiceNow task table.
    """
    print("\n[INFO] Fetching unassigned tasks...")
    endpoint = "/api/now/table/task"
    params = {
        "sysparm_query": "assigned_toISEMPTY",
        "sysparm_limit": "10"
    }
    return get_servicenow_data(endpoint, params)

def get_change_tasks():
    """
    Retrieves change tasks from the ServiceNow change_task table.
    """
    print("\n[INFO] Fetching change tasks...")
    endpoint = "/api/now/table/change_task"
    params = {
        "sysparm_limit": "10"
    }
    return get_servicenow_data(endpoint, params)

def export_to_file(data, filename):
    """
    Exports the given data to a human-readable text file.
    """
    with open(filename, 'w') as file:
        for section, items in data.items():
            file.write(f"{section}:\n")
            if "error" in items:
                file.write(f"Error: {items['error']}\n")
            else:
                for item in items.get('result', []):
                    file.write(f"Task Number: {item.get('number', 'N/A')}\n")
                    file.write(f"Short Description: {item.get('short_description', 'N/A')}\n")
                    file.write("\n")
            file.write("\n")
    print(f"[SUCCESS] Data exported to {filename}")

# Main execution
if __name__ == "__main__":
    results = {}
    unassigned_tasks = get_unassigned_tasks()
    results["Unassigned Tasks"] = unassigned_tasks
    print("[RESULT] Unassigned Tasks:\n", unassigned_tasks)

    change_tasks = get_change_tasks()
    results["Change Tasks"] = change_tasks
    print("[RESULT] Change Tasks:\n", change_tasks)

    export_to_file(results, "servicenow_output1.txt")

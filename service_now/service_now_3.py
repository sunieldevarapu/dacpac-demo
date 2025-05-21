import os
import requests
from requests.auth import HTTPBasicAuth

# Base configuration
INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "https://your_instance.service-now.com")
USERNAME = os.getenv("SERVICENOW_USERNAME", "your_username")
PASSWORD = os.getenv("SERVICENOW_PASSWORD", "your_password")

def get_servicenow_data(endpoint, params=None):
    """
    Makes a GET request to the ServiceNow API using basic authentication.
    """
    url = f"{INSTANCE_URL}{endpoint}"
    headers = {"Accept": "application/json"}
    print(f"[INFO] GET Request: {url}")
    if params:
        print(f"[INFO] Parameters: {params}")
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, params=params)
        response.raise_for_status()
        print("[SUCCESS] Data retrieved.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] GET failed: {e}")
        return {"error": str(e)}

def assign_servicenow_item(table, sys_id, user_sys_id):
    """
    Assigns a task to a user by updating the 'assigned_to' field.
    """
    print(f"\n[INFO] Assigning item {sys_id} in table {table} to user {user_sys_id}")
    url = f"{INSTANCE_URL}/api/now/table/{table}/{sys_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "assigned_to": user_sys_id
    }
    try:
        response = requests.patch(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, json=payload)
        response.raise_for_status()
        print("[SUCCESS] Task assigned.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Assignment failed: {e}")
        return {"error": str(e)}

def retrieve_servicenow_items(table, query=None, limit=10):
    """
    Retrieves items from any ServiceNow table.
    """
    print(f"\n[INFO] Retrieving items from table: {table}")
    endpoint = f"/api/now/table/{table}"
    params = {
        "sysparm_limit": str(limit)
    }
    if query:
        params["sysparm_query"] = query
    return get_servicenow_data(endpoint, params)

def get_action_items():
    """
    Retrieves tasks with keywords like Deploy, Release, Manual, or Skip.
    """
    print("\n[INFO] Searching for action items...")
    keywords = ["Deploy", "Release", "Manual", "Skip"]
    query_parts = [f"short_descriptionLIKE{kw}" for kw in keywords]
    query = "^OR".join(query_parts)
    return retrieve_servicenow_items("task", query=query, limit=20)

def get_unassigned_tasks():
    print("\n[INFO] Fetching unassigned tasks...")
    return retrieve_servicenow_items("task", query="assigned_toISEMPTY", limit=10)

def get_change_tasks():
    print("\n[INFO] Fetching change tasks...")
    return retrieve_servicenow_items("change_task", limit=10)

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

    unassigned = get_unassigned_tasks()
    results["Unassigned Tasks"] = unassigned
    print("[RESULT] Unassigned Tasks:\n", unassigned)

    changes = get_change_tasks()
    results["Change Tasks"] = changes
    print("[RESULT] Change Tasks:\n", changes)

    actions = get_action_items()
    results["Action Items"] = actions
    print("[RESULT] Action Items:\n", actions)

    # Example: Assign a task (replace with actual sys_id and user_sys_id)
    # assigned = assign_servicenow_item("task", "some_sys_id", "user_sys_id")
    # print("[RESULT] Assignment Response:\n", assigned)

    # Export results to a file
    export_to_file(results, "servicenow_output.txt")

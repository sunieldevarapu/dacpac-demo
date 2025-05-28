import requests
import subprocess
import os
from datetime import datetime, timezone

# Configuration (can be loaded from environment variables)
SERVICENOW_URL = os.getenv("SN_URL")  # e.g., https://yourinstance.service-now.com
SN_USERNAME = os.getenv("SN_USERNAME")
SN_PASSWORD = os.getenv("SN_PASSWORD")

OCTOPUS_SERVER = os.getenv("OCTOPUS_SERVER")
OCTOPUS_API_KEY = os.getenv("OCTOPUS_API_KEY")
PROJECT_NAME = os.getenv("OCTOPUS_PROJECT")        # e.g., "MyApp"
RELEASE_VERSION = os.getenv("OCTOPUS_RELEASE")     # e.g., "1.0.0"
ENVIRONMENT = os.getenv("OCTOPUS_ENVIRONMENT")     # e.g., "Production"
CTASK_ID = os.getenv("CTASK_ID")                   # e.g., "CTASK0012345"
TENANT_NAME = os.getenv("OCTOPUS_TENANT", "")      # Optional

# Optional: assign CTASK to a user
ASSIGNEE_SYS_ID = os.getenv("SN_ASSIGNEE_SYS_ID", "")  # e.g., sys_id of user

def get_ctask_details(ctask_id):
    url = f"{SERVICENOW_URL}/api/now/table/change_task?sysparm_query=number={ctask_id}"
    response = requests.get(url, auth=(SN_USERNAME, SN_PASSWORD), headers={"Accept": "application/json"})

    if response.status_code == 200:
        data = response.json()
        if data["result"]:
            task = data["result"][0]
            return {
                "sys_id": task["sys_id"],
                "number": task["number"],
                "short_description": task["short_description"],
                "start_time": task["start_date"],  # Expected format: "YYYY-MM-DD HH:MM:SS"
                "assigned_to": task["assigned_to"]
            }
        else:
            print(f"No CTASK found for ID: {ctask_id}")
    else:
        print(f"Failed to fetch CTASK: {response.status_code} - {response.text}")
    return None

def assign_ctask(sys_id, assignee_sys_id):
    url = f"{SERVICENOW_URL}/api/now/table/change_task/{sys_id}"
    response = requests.patch(
        url,
        auth=(SN_USERNAME, SN_PASSWORD),
        headers={"Content-Type": "application/json"},
        json={"assigned_to": assignee_sys_id}
    )
    if response.status_code == 200:
        print(f"CTASK {sys_id} assigned successfully.")
        return True
    else:
        print(f"Failed to assign CTASK: {response.status_code} - {response.text}")
        return False

def schedule_octopus_deployment(deployment_time_utc):
    cli_cmd = [
        "octo", "deploy-release",
        "--project", PROJECT_NAME,
        "--releaseNumber", RELEASE_VERSION,
        "--deployTo", ENVIRONMENT,
        "--server", OCTOPUS_SERVER,
        "--apiKey", OCTOPUS_API_KEY,
        "--guidedFailure=false",
        "--deploymentTime", deployment_time_utc
    ]

    if TENANT_NAME:
        cli_cmd += ["--tenants", TENANT_NAME]

    print("Running Octopus CLI command...")
    print(" ".join(cli_cmd))
    result = subprocess.run(cli_cmd, capture_output=True, text=True)

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    if result.returncode == 0:
        print("Deployment scheduled successfully.")
    else:
        print("Deployment failed to schedule.")

def main():
    ctask = get_ctask_details(CTASK_ID)
    if not ctask:
        return

    print(f"CTASK Found: {ctask['number']} - {ctask['short_description']}")
    print(f"Start Time: {ctask['start_time']}")

    # Optionally assign task
    if ASSIGNEE_SYS_ID:
        assign_ctask(ctask["sys_id"], ASSIGNEE_SYS_ID)

    # Convert CTASK start_time to ISO 8601 UTC format for Octopus
    try:
        dt_local = datetime.strptime(ctask["start_time"], "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_local.astimezone(timezone.utc)
        deployment_time_utc = dt_utc.isoformat(timespec='seconds').replace("+00:00", "Z")

        print(f"Deployment UTC Time: {deployment_time_utc}")
        schedule_octopus_deployment(deployment_time_utc)
    except Exception as e:
        print("Error parsing date:", e)

if __name__ == "__main__":
    main()

import requests
import json
from datetime import datetime
import pytz

# Helper function to print timestamped messages
def print_timestamped(message):
    central = pytz.timezone("US/Central")
    now = datetime.now(pytz.utc).astimezone(central)
    print(f"{message} {now.strftime('%Y-%m-%d %H:%M')} CST")
    print("-" * 20)

# Sample data
unassigned_tasks = [
    {"id": "CTASK001", "description": "Update deployment pipeline"},
    {"id": "CTASK002", "description": "Review change request"}
]

assigned_tasks = [
    {"id": "CTASK003", "description": "Deploy to staging"},
    {"id": "CTASK004", "description": "Deploy to production"}
]

queued_deployments = [
    {"id": "DEPLOY001", "project": "Project A"},
    {"id": "DEPLOY002", "project": "Project B"}
]

def unassign_tasks():
    print("Starting task unassignment...")
    print_timestamped("PROCESS STARTED")
    print("ENVIRONMENT: development")
    print("Unassigning tasks assigned to AUTOOCTOPUS...")
    for task in assigned_tasks:
        print(f"Unassigned task: {task['id']} - {task['description']}")
    print_timestamped("UNASSIGN")

def schedule_tasks():
    print("Fetching unassigned tasks...")
    for task in unassigned_tasks:
        print(f"Unassigned task: {task['id']} - {task['description']}")
    print_timestamped("GET TASKS")
    if unassigned_tasks:
        print("Scheduling tasks...")
        for task in unassigned_tasks:
            print(f"Scheduled task: {task['id']} - {task['description']}")
        print_timestamped("SCHEDULE")
    else:
        print("No unassigned tasks found.")

def authorize_deployments():
    print("Fetching queued deployments...")
    for deploy in queued_deployments:
        print(f"Queued deployment: {deploy['id']} - {deploy['project']}")
    print_timestamped("GET QUEUED DEPLOYMENTS")

    print("Fetching assigned tasks...")
    for task in assigned_tasks:
        print(f"Assigned task: {task['id']} - {task['description']}")
    print_timestamped("GET ASSIGNED TASKS")

    print("Authorizing deployments...")
    for deploy in queued_deployments:
        print(f"Authorized deployment: {deploy['id']} for project {deploy['project']}")
    print_timestamped("AUTHORIZE DEPLOYMENTS")
    print_timestamped("PROCESS FINISHED")

def schedule_octopus_deployment():
    print("Starting Octopus deployment scheduling...")
    octopus_url = "https://your-octopus-instance.octopus.app"
    api_key = "API-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    project_id = "Projects-123"
    release_id = "Releases-456"
    environment_id = "Environments-789"
    queue_time = "2025-05-20T10:00:00-05:00"

    headers = {
        "X-Octopus-ApiKey": api_key,
        "Content-Type": "application/json"
    }

    body = {
        "ReleaseId": release_id,
        "ProjectId": project_id,
        "EnvironmentId": environment_id,
        "QueueTime": queue_time
    }

    try:
        response = requests.post(f"{octopus_url}/api/deployments", headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        print("Deployment successfully scheduled!")
        print(f"Deployment ID: {data.get('Id')}")
    except requests.exceptions.RequestException as e:
        print("Failed to schedule deployment.")
        print(f"Error: {e}")
        exit(1)

    print_timestamped("OCTOPUS DEPLOYMENT SCHEDULED")

# Execute all steps
print("Executing workflow steps...")
unassign_tasks()
schedule_tasks()
authorize_deployments()
schedule_octopus_deployment()
print("Workflow completed successfully!")

import requests
import json
from datetime import datetime

# Constants (replace with secure retrieval in production)
API_KEY = "API-"
BASE_URL = "https://octopusdeploy"
HEADERS = {
    "X-Octopus-ApiKey": API_KEY,
    "Content-Type": "application/json"
}

def list_projects():
    url = f"{BASE_URL}/api/projects?take=999"
    response = requests.get(url, headers=HEADERS, verify=False)
    projects = response.json().get("Items", [])
    for project in projects:
        print(project["Name"])
    return projects

def get_project_by_id(projects, project_id):
    return next((p for p in projects if p["Id"] == project_id), None)

def get_latest_release(project_id):
    url = f"{BASE_URL}/api/projects/{project_id}/releases"
    response = requests.get(url, headers=HEADERS, verify=False)
    releases = response.json().get("Items", [])
    return releases[0]["Id"] if releases else None

def get_channel_id(project_id):
    url = f"{BASE_URL}/api/projects/{project_id}/channels"
    response = requests.get(url, headers=HEADERS, verify=False)
    channels = response.json().get("Items", [])
    return channels[0]["Id"] if channels else None

def create_release(project_id, channel_id):
    url = f"{BASE_URL}/api/Spaces-1/releases/create/v1"
    payload = {
        "Version": "0.37",
        "ProjectID": project_id,
        "ChannelID": channel_id,
        "SpaceID": "Spaces-1",
        "ProjectName": "Liquibase - Deploy - Demo",
        "SpaceIdOrName": "Spaces-1"
    }
    response = requests.post(url, headers=HEADERS, json=payload, verify=False)
    print("Release Created:", response.json())

def prepare_deployment(project_id, release_id, channel_id):
    url = f"{BASE_URL}/api/Spaces-1/deployments"
    payload = {
        "ProjectId": project_id,
        "ReleaseId": release_id,
        "EnvironmentId": "Environments-2",
        "ChannelId": channel_id,
        "QueueTime": "2025-05-14T21:55:00Z",
        "QueueTimeExpiry": "2025-05-14T22:55:00Z"
    }
    response = requests.post(url, headers=HEADERS, json=payload, verify=False)
    print("Deployment Prepared:", response.json())

if __name__ == "__main__":
    project_id = "Projects-184"
    projects = list_projects()
    project = get_project_by_id(projects, project_id)
    if not project:
        print(f"Project {project_id} not found.")
        exit(1)

    release_id = get_latest_release(project_id)
    channel_id = get_channel_id(project_id)

    create_release(project_id, channel_id)
    prepare_deployment(project_id, release_id, channel_id)

=======================================================================


def list_projects():
    print("🔍 Fetching all projects from Octopus Deploy...")
    url = f"{BASE_URL}/api/projects?take=999"
    response = requests.get(url, headers=HEADERS, verify=False)
    projects = response.json().get("Items", [])
    print(f"✅ Found {len(projects)} projects.")
    for project in projects:
        print(f"   - {project['Name']}")
    return projects

def get_project_by_id(projects, project_id):
    print(f"🔎 Searching for project with ID: {project_id}")
    project = next((p for p in projects if p["Id"] == project_id), None)
    if project:
        print(f"✅ Project found: {project['Name']}")
    else:
        print("❌ Project not found.")
    return project

def get_latest_release(project_id):
    print(f"📦 Fetching latest release for project ID: {project_id}")
    url = f"{BASE_URL}/api/projects/{project_id}/releases"
    response = requests.get(url, headers=HEADERS, verify=False)
    releases = response.json().get("Items", [])
    if not releases:
        print("❌ No releases found.")
        return None
    latest_release_id = releases[0]["Id"]
    print(f"✅ Latest release ID: {latest_release_id}")
    return latest_release_id

def get_channel_id(project_id):
    print(f"📡 Fetching channel ID for project ID: {project_id}")
    url = f"{BASE_URL}/api/projects/{project_id}/channels"
    response = requests.get(url, headers=HEADERS, verify=False)
    channels = response.json().get("Items", [])
    if not channels:
        print("❌ No channels found.")
        return None
    channel_id = channels[0]["Id"]
    print(f"✅ Channel ID: {channel_id}")
    return channel_id

def create_release(project_id, channel_id):
    print(f"🚀 Creating release for project ID: {project_id}")
    url = f"{BASE_URL}/api/Spaces-1/releases/create/v1"
    payload = {
        "Version": "0.37",
        "ProjectID": project_id,
        "ChannelID": channel_id,
        "SpaceID": "Spaces-1",
        "ProjectName": "Liquibase - Deploy - Demo",
        "SpaceIdOrName": "Spaces-1"
    }
    response = requests.post(url, headers=HEADERS, json=payload, verify=False)
    print("✅ Release creation response:")
    print(json.dumps(response.json(), indent=2))

def prepare_deployment(project_id, release_id, channel_id):
    print(f"🛠️ Preparing deployment for project ID: {project_id}")
    url = f"{BASE_URL}/api/Spaces-1/deployments"
    payload = {
        "ProjectId": project_id,
        "ReleaseId": release_id,
        "EnvironmentId": "Environments-2",
        "ChannelId": channel_id,
        "QueueTime": "2025-05-14T21:55:00Z",
        "QueueTimeExpiry": "2025-05-14T22:55:00Z"
    }
    response = requests.post(url, headers=HEADERS, json=payload, verify=False)
    print("✅ Deployment preparation response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("🏁 Starting Octopus Deploy automation script...\n")
    project_id = "Projects-184"
    projects = list_projects()
    project = get_project_by_id(projects, project_id)
    if not project:
        print("❌ Exiting script due to missing project.")
        exit(1)

    release_id = get_latest_release(project_id)
    if not release_id:
        print("❌ Exiting script due to missing release.")
        exit(1)

    channel_id = get_channel_id(project_id)
    if not channel_id:
        print("❌ Exiting script due to missing channel.")
        exit(1)

    create_release(project_id, channel_id)
    prepare_deployment(project_id, release_id, channel_id)
    print("\n✅ Script execution completed.")


import argparse
import os
import requests
from datetime import datetime, timedelta
import sys


# ---------------------------
# Configuration (from env)
# ---------------------------
BASE_URL = 'https://octopus.company.com'
PROJECTS_ENDPOINT = '/api/projects/all'
DEPLOYMENT_ENDPOINT = '/api/deployments'
RELEASES_ENDPOINT_TEMPLATE = '/api/projects/{project_id}/releases?take=999'

OCTOPUS_API_KEY = os.environ.get('OCTOPUS_DEPLOY_API_KEY')
OCTOPUS_ENVIRONMENT_ID = os.environ.get('OCTOPUS_ENVIRONMENT_ID')

HEADERS = {
    "X-Octopus-ApiKey": OCTOPUS_API_KEY,
    "Content-Type": "application/json"
}

# ---------------------------
# Helpers
# ---------------------------
def find_project_id(project_name):
    print(f"Finding project ID for: {project_name}")
    url = f"{BASE_URL}{PROJECTS_ENDPOINT}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    for project in response.json().get("Items", []):
        if project["Name"] == project_name:
            print(f"Found project ID: {project['Id']}")
            return project["Id"]

    raise Exception(f"Project '{project_name}' not found.")


def find_release_info(project_id, version):
    print(f"Finding release info for version: {version}")
    url = f"{BASE_URL}/api/projects/{project_id}/releases?take=999"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    for release in response.json().get("Items", []):
        if release["Version"] == version:
            print(f"Found release ID: {release['Id']}, Channel ID: {release['ChannelId']}")
            return release["Id"], release["ChannelId"]

    raise Exception(f"Release '{version}' not found for project ID '{project_id}'.")


def prepare_times(deployment_time_str):
    print(f"Preparing times for deployment at: {deployment_time_str}")
    try:
        local_dt = datetime.strptime(deployment_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Deployment time must be in format 'YYYY-MM-DD HH:MM:SS'")

    queue_time = local_dt.astimezone().isoformat()
    expiry_time = (local_dt + timedelta(minutes=30)).astimezone().isoformat()

    print(f"Queue Time: {queue_time}")
    print(f"Queue Time Expiry: {expiry_time}")
    return queue_time, expiry_time


def schedule_deployment(project_id, release_id, channel_id, queue_time, expiry_time):
    print("Scheduling deployment...")
    payload = {
        "ReleaseId": release_id,
        "ProjectId": project_id,
        "ChannelId": channel_id,
        "EnvironmentId": OCTOPUS_ENVIRONMENT_ID,
        "QueueTime": queue_time,
        "QueueTimeExpiry": expiry_time
    }

    response = requests.post(
        f"{BASE_URL}{DEPLOYMENT_ENDPOINT}",
        headers=HEADERS,
        json=payload
    )

    if response.status_code not in (200, 201):
        print("Error:", response.text)
        raise Exception("Failed to schedule deployment")

    deployment_id = response.json().get("Id")
    if not deployment_id:
        raise Exception("Deployment ID not returned")

    print(f"✅ Successfully scheduled deployment (ID: {deployment_id})")


# ---------------------------
# Main Script Logic
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Octopus Deploy scheduler")
    parser.add_argument('--action', required=True, choices=['schedule', 'deploy'])
    parser.add_argument('--releaseNumber', help='Release number (required for deploy)')
    parser.add_argument('--projectName', help='Project name (required for deploy)')
    parser.add_argument('--deploymentTime', help='Deployment time in "YYYY-MM-DD HH:MM:SS" (required for deploy)')

    args = parser.parse_args()

    if args.action == 'deploy':
        if not all([args.releaseNumber, args.projectName, args.deploymentTime]):
            print("Error: For 'deploy', --releaseNumber, --projectName, and --deploymentTime are required.")
            sys.exit(1)

        if not OCTOPUS_API_KEY or not OCTOPUS_ENVIRONMENT_ID:
            print("Error: Required environment variables are not set (OCTOPUS_DEPLOY_API_KEY, OCTOPUS_ENVIRONMENT_ID).")
            sys.exit(1)

        project_id = find_project_id(args.projectName)
        release_id, channel_id = find_release_info(project_id, args.releaseNumber)
        queue_time, expiry_time = prepare_times(args.deploymentTime)
        schedule_deployment(project_id, release_id, channel_id, queue_time, expiry_time)
    else:
        print("Action 'schedule' is not implemented in this script yet.")


if __name__ == '__main__':
    main()

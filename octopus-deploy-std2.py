import requests

# ----------------------------
# Hardcoded Octopus Deploy Config
# ----------------------------
OCTOPUS_API_KEY = "API-XXXXXXXXXXXXXXXXXXXXXXX"
OCTOPUS_SERVER = "https://your-octopus-server.com"
HEADERS = {
    "X-Octopus-ApiKey": OCTOPUS_API_KEY,
    "Content-Type": "application/json"
}

PROJECT_NAME = "YourProject"
ENVIRONMENT_NAME = "Production"
RELEASE_VERSION = "1.0.0"
SPACE_NAME = "Default"

# ----------------------------
# Utility Functions
# ----------------------------

def get_space_id():
    response = requests.get(f"{OCTOPUS_SERVER}/api/spaces", headers=HEADERS)
    response.raise_for_status()
    spaces = response.json()["Items"]
    space = next((s for s in spaces if s["Name"] == SPACE_NAME), None)
    if not space:
        raise Exception(f"Space '{SPACE_NAME}' not found.")
    return space["Id"]

def get_project_id(space_id):
    url = f"{OCTOPUS_SERVER}/api/{space_id}/projects/all"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    projects = response.json()
    project = next((p for p in projects if p["Name"] == PROJECT_NAME), None)
    if not project:
        raise Exception(f"Project '{PROJECT_NAME}' not found.")
    return project["Id"]

def get_environment_id(space_id):
    url = f"{OCTOPUS_SERVER}/api/{space_id}/environments/all"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    environments = response.json()
    env = next((e for e in environments if e["Name"] == ENVIRONMENT_NAME), None)
    if not env:
        raise Exception(f"Environment '{ENVIRONMENT_NAME}' not found.")
    return env["Id"]

def create_release(space_id, project_id):
    url = f"{OCTOPUS_SERVER}/api/{space_id}/releases"
    payload = {
        "ProjectId": project_id,
        "Version": RELEASE_VERSION
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 409:
        print(f"Release {RELEASE_VERSION} already exists.")
    else:
        response.raise_for_status()
        print(f"Release {RELEASE_VERSION} created.")

def deploy_release(space_id, project_id, environment_id):
    url = f"{OCTOPUS_SERVER}/api/{space_id}/deployments"
    payload = {
        "ProjectId": project_id,
        "ReleaseId": f"Releases-{RELEASE_VERSION}",
        "EnvironmentId": environment_id
    }
    # Lookup release ID
    release_url = f"{OCTOPUS_SERVER}/api/{space_id}/projects/{project_id}/releases"
    releases = requests.get(release_url, headers=HEADERS).json()["Items"]
    release = next((r for r in releases if r["Version"] == RELEASE_VERSION), None)
    if not release:
        raise Exception(f"Release {RELEASE_VERSION} not found.")
    payload["ReleaseId"] = release["Id"]

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    print(f"Deployment started to {ENVIRONMENT_NAME}.")

# ----------------------------
# Main Execution
# ----------------------------

def main():
    print("Starting Octopus Deployment Script...")
    space_id = get_space_id()
    project_id = get_project_id(space_id)
    environment_id = get_environment_id(space_id)
    create_release(space_id, project_id)
    deploy_release(space_id, project_id, environment_id)
    print("Deployment process completed.")

if __name__ == "__main__":
    main()

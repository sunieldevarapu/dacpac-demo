import json
import os
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import requests
import zipfile
import urllib3
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

queue_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
queue_expiry = (datetime.now(timezone.utc) + timedelta(minutes=65)).strftime("%Y-%m-%dT%H:%M:%SZ")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "API-"
BASE_URL = "https://octopusdeploy-dev"
HEADERS = {
    "X-Octopus-ApiKey": API_KEY,
    "Content-Type": "application/json"
}

def run_cmd(command, shell=True, check=True):
    print(f"\n>>> Running command: {command}")
    try:
        subprocess.run(command, shell=shell, check=check)
        print(f">>> Success: {command}")
    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR running command: {command}")
        print(f"Return code: {e.returncode}")
        raise

def load_env():
    print("🔄 Loading environment variables from .env...")
    load_dotenv()

def set_version():
    print("\n📦 Setting PACKAGE_VERSION...")
    run_number = os.getenv('GITHUB_RUN_NUMBER', '1')
    version = datetime.now().strftime("%Y.%m.%d") + f".{run_number}"
    os.environ["PACKAGE_VERSION"] = version
    print(f"✔ PACKAGE_VERSION set to: {version}")
    return version

def install_dependencies():
    print("\n📦 Installing Python dependencies...")
    run_cmd("python -m pip install --upgrade pip")
    run_cmd("pip install -r requirements.txt")

def run_tests():
    print("\n🧪 Running unit tests...")
    run_cmd("python -m unittest discover -s tests")

def create_artifacts_folder():
    print("\n📁 Creating artifacts folder structure...")
    Path("artifacts/TestApp").mkdir(parents=True, exist_ok=True)
    print("✔ Created 'artifacts/TestApp'")

def copy_app_files():
    print("\n📂 Copying application files...")
    src_dir = "test_app"
    dest_dir = "artifacts/TestApp"
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        print(f"✔ Copied files from '{src_dir}' to '{dest_dir}'")
    else:
        raise FileNotFoundError(f"❌ Source directory '{src_dir}' not found.")

def install_octopus_cli():
    print("\n🔧 Installing Octopus CLI (manual method)...")
    octo_url = "https://github.com/OctopusDeploy/OctopusCLI/releases/download/v9.1.7/OctopusTools.9.1.7.win-x64.zip"
    octo_zip = "OctopusTools.zip"
    extract_dir = "octo-cli"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PythonScript"
    }

    # Step 1: Download the CLI zip
    print(f"⬇ Downloading Octopus CLI from: {octo_url}")
    response = requests.get(octo_url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"❌ Failed to download Octopus CLI: HTTP {response.status_code}")

    with open(octo_zip, "wb") as f:
        f.write(response.content)
    print(f"✔ Saved ZIP as: {octo_zip}")

    # Step 2: Extract contents
    print(f"📦 Extracting ZIP to '{extract_dir}'...")
    with zipfile.ZipFile(octo_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("✔ Extraction complete.")

    # Step 3: Add to PATH
    full_path = os.path.abspath(extract_dir)
    os.environ["PATH"] = f"{full_path};{os.environ['PATH']}"
    print(f"🔁 Added Octopus CLI to PATH: {full_path}")

    # Step 4: Verify installation
    print("✅ Verifying CLI with 'octo help'...")
    run_cmd("octo help")

def list_projects():
    print("Fetching all projects from Octopus Deploy...")
    url = f"{BASE_URL}/api/projects?take=999"
    response = requests.get(url, headers=HEADERS, verify=False)
    projects = response.json().get("Items", [])
    print(f"Found {len(projects)} projects.")
    for project in projects:
        print(f"   - {project['Name']}")
    return projects

def get_project_by_id(projects, project_id):
    print(f"Searching for project with ID: {project_id}")
    project = next((p for p in projects if p["Id"] == project_id), None)
    if project:
        print(f"Project found: {project['Name']}")
    else:
        print("Project not found.")
    return project

def get_latest_release(project_id):
    print(f"Fetching latest release for project ID: {project_id}")
    url = f"{BASE_URL}/api/projects/{project_id}/releases"
    response = requests.get(url, headers=HEADERS, verify=False)
    releases = response.json().get("Items", [])
    if not releases:
        print("No releases found.")
        return None
    latest_release_id = releases[0]["Id"]
    print(f"Latest release ID: {latest_release_id}")
    return latest_release_id

def get_channel_id(project_id):
    print(f"📡 Fetching channel ID for project ID: {project_id}")
    url = f"{BASE_URL}/api/projects/{project_id}/channels"
    response = requests.get(url, headers=HEADERS, verify=False)
    channels = response.json().get("Items", [])
    if not channels:
        print("No channels found.")
        return None
    channel_id = channels[0]["Id"]
    print(f"Channel ID: {channel_id}")
    return channel_id

def create_release(project_id, channel_id):
    print(f"Creating release for project ID: {project_id}")
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
    print("Release creation response:")
    print(json.dumps(response.json(), indent=2))

def prepare_deployment(project_id, release_id, channel_id):
    print(f"Preparing deployment for project ID: {project_id}")
    url = f"{BASE_URL}/api/Spaces-1/deployments"
    payload = {
        "ProjectId": project_id,
        "ReleaseId": release_id,
        "EnvironmentId": "Environments-2",
        "ChannelId": channel_id,
        "QueueTime": queue_time,
        "QueueTimeExpiry": queue_expiry
    }
    response = requests.post(url, headers=HEADERS, json=payload, verify=False)
    print("Deployment preparation response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("=== 🛠 Python Build & Deployment Script Starting ===")
    load_env()

    parser = argparse.ArgumentParser(description="Python Build and Deployment Script")
    parser.add_argument('--all', action='store_true', help="Run full pipeline: test + package + deploy")
    parser.add_argument('--test', action='store_true', help="Install dependencies and run tests")
    parser.add_argument('--package', action='store_true', help="Create artifacts and package app")
    parser.add_argument('--deploy-only', action='store_true', help="Push, release, and deploy only")
    args = parser.parse_args()

    version = set_version()

    if args.all:
        print("\n[MODE] Running full pipeline (--all)")
        install_dependencies()
        run_tests()
        create_artifacts_folder()
        copy_app_files()
        install_octopus_cli()
        # package_app(version)
        # push_package(version)
        # create_release(version)
        # deploy_release(version)
        print("Starting Octopus Deploy automation script...\n")
        project_id = "Projects-184"
        projects = list_projects()
        project = get_project_by_id(projects, project_id)
        if not project:
            print("Exiting script due to missing project.")
            exit(1)
        release_id = get_latest_release(project_id)
        if not release_id:
            print("Exiting script due to missing release.")
            exit(1)
        channel_id = get_channel_id(project_id)
        if not channel_id:
            print("Exiting script due to missing channel.")
            exit(1)
        create_release(project_id, channel_id)
        prepare_deployment(project_id, release_id, channel_id)
        

    elif args.test:
        print("\n[MODE] Test mode (--test)")
        install_dependencies()
        run_tests()

    # elif args.package:
    #     print("\n[MODE] Package mode (--package)")
    #     create_artifacts_folder()
    #     copy_app_files()
    #     install_octopus_cli()
    #     package_app(version)

    # elif args.deploy_only:
    #     print("\n[MODE] Deploy-only mode (--deploy-only)")
    #     push_package(version)
    #     create_release(version)
    #     deploy_release(version)

    else:
        print("\n[ERROR] No valid option provided.")
        parser.print_help()

    print("\nScript execution completed.")

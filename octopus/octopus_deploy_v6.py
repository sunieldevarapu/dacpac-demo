import os
import argparse
import subprocess
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
print("Loading environment variables from .env...")
load_dotenv()

def run_cmd(command, shell=True, check=True):
    print(f"\n>>> Running command: {command}")
    try:
        subprocess.run(command, shell=shell, check=check)
        print(f">>> Success: {command}")
    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR running command: {command}")
        print(f"Return code: {e.returncode}")
        raise

def set_version():
    print("\n--- Setting PACKAGE_VERSION...")
    run_number = os.getenv('GITHUB_RUN_NUMBER', '1')
    version = datetime.now().strftime("%Y.%m.%d") + f".{run_number}"
    os.environ["PACKAGE_VERSION"] = version
    print(f"PACKAGE_VERSION set to: {version}")
    return version

def install_dependencies():
    print("\n--- Installing dependencies...")
    run_cmd("python -m pip install --upgrade pip")
    run_cmd("pip install -r requirements.txt")
    print("Dependencies installed.")

def run_tests():
    print("\n--- Running unit tests...")
    run_cmd("python -m unittest discover -s tests")
    print("Tests completed.")

def create_artifacts_folder():
    print("\n--- Creating artifacts folders...")
    try:
        os.makedirs("artifacts/TestApp", exist_ok=True)
        print("Created 'artifacts/TestApp'")
    except Exception as e:
        print(f"Failed to create artifacts folders: {e}")
        raise

def copy_app_files():
    print("\n--- Copying application files to artifacts folder...")
    src_dir = "test_app"
    dest_dir = "artifacts/TestApp"
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        print(f"Copied files from {src_dir} to {dest_dir}")
    else:
        print(f"!!! ERROR: Source directory '{src_dir}' does not exist.")
        raise FileNotFoundError(f"{src_dir} not found.")

def install_octopus_cli():
    print("\n--- Installing Octopus CLI via dotnet tool...")
    run_cmd("dotnet tool install --global OctopusTools")
    print("Octopus CLI installed.")

def package_app(version):
    print("\n--- Packaging application with Octopus CLI...")
    command = (
        f'octo pack --id="TestApp" '
        f'--format="Zip" '
        f'--version="{version}" '
        f'--basePath="artifacts/TestApp" '
        f'--outFolder="artifacts"'
    )
    run_cmd(command)
    print(f"App packaged: artifacts/TestApp.{version}.zip")

def push_package(version):
    print("\n--- Pushing package to Octopus Deploy...")
    api_key = os.getenv("OCTOPUSSERVERAPIKEY")
    server = os.getenv("OCTOPUSSERVERURL")
    space = os.getenv("OCTOPUSSERVER_SPACE")
    package_path = f"artifacts/TestApp.{version}.zip"

    print(f"Using server: {server}")
    print(f"Using space: {space}")
    print(f"Pushing package: {package_path}")

    command = (
        f'octo push --server="{server}" '
        f'--apiKey="{api_key}" '
        f'--space="{space}" '
        f'--package="{package_path}" '
        f'--overwrite-mode=OverwriteExisting'
    )
    run_cmd(command)
    print("Package pushed successfully.")

def create_release(version):
    print("\n--- Creating Octopus release...")
    command = (
        f'octo create-release --project="TestProject" '
        f'--version="{version}" '
        f'--server="{os.environ["OCTOPUSSERVERURL"]}" '
        f'--apiKey="{os.environ["OCTOPUSSERVERAPIKEY"]}" '
        f'--space="{os.environ["OCTOPUSSERVER_SPACE"]}"'
    )
    run_cmd(command)
    print(f"Release created for version: {version}")

def deploy_release(version):
    print("\n--- Deploying release to environment: Test")
    command = (
        f'octo deploy-release --project="TestProject" '
        f'--version="{version}" '
        f'--server="{os.environ["OCTOPUSSERVERURL"]}" '
        f'--apiKey="{os.environ["OCTOPUSSERVERAPIKEY"]}" '
        f'--space="{os.environ["OCTOPUSSERVER_SPACE"]}" '
        f'--deployTo="Test"'
    )
    run_cmd(command)
    print("Deployment triggered.")

if __name__ == "__main__":
    print("=== Python Build & Deployment Script Starting ===")
    
    parser = argparse.ArgumentParser(description="Python Build and Deployment Script")
    parser.add_argument('--all', action='store_true', help="Run full build + test + deploy process")
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
        package_app(version)
        push_package(version)
        create_release(version)
        deploy_release(version)

    elif args.test:
        print("\n[MODE] Running test-only mode (--test)")
        install_dependencies()
        run_tests()

    elif args.package:
        print("\n[MODE] Running package-only mode (--package)")
        create_artifacts_folder()
        copy_app_files()
        install_octopus_cli()
        package_app(version)

    elif args.deploy_only:
        print("\n[MODE] Running deploy-only mode (--deploy-only)")
        push_package(version)
        create_release(version)
        deploy_release(version)

    else:
        print("\n[ERROR] No command selected.")
        parser.print_help()

    print("\n=== Script Finished ===")


=========================================================================

def install_octopus_cli():
    print("\n--- Installing Octopus CLI manually (Windows)...")

    octo_url = "https://download.octopusdeploy.com/octopus-tools/OctopusTools.latest.zip"
    octo_zip = "OctopusTools.zip"
    extract_dir = "octo-cli"

    # Download CLI zip
    run_cmd(f"curl -L -o {octo_zip} {octo_url}")

    # Extract to folder
    shutil.unpack_archive(octo_zip, extract_dir)
    print(f"Extracted Octopus CLI to {extract_dir}")

    # Add CLI path to environment PATH
    octo_path = os.path.abspath(extract_dir)
    os.environ["PATH"] = f"{octo_path};{os.environ['PATH']}"
    print(f"Added {octo_path} to PATH")

    # Optionally verify installation
    run_cmd("octo help")


=======================================================================================================

def install_octopus_cli():
    print("\n--- Installing Octopus CLI manually (Windows)...")

    # Octopus CLI direct ZIP download for Windows x64
    octo_url = "https://download.octopusdeploy.com/octopus-tools/OctopusTools.8.4.0-win-x64.zip"
    octo_zip = "OctopusTools.zip"
    extract_dir = "octo-cli"

    # Step 1: Download the CLI zip using requests (not curl)
    import requests
    print(f"Downloading Octopus CLI from {octo_url}...")
    response = requests.get(octo_url)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download Octopus CLI: {response.status_code}")
    
    with open(octo_zip, "wb") as f:
        f.write(response.content)
    print(f"Saved ZIP as: {octo_zip}")

    # Step 2: Extract ZIP contents using zipfile
    import zipfile
    print(f"Extracting {octo_zip} to {extract_dir}...")
    with zipfile.ZipFile(octo_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Extraction complete.")

    # Step 3: Add extracted folder to PATH
    octo_path = os.path.abspath(extract_dir)
    os.environ["PATH"] = f"{octo_path};{os.environ['PATH']}"
    print(f"Added {octo_path} to PATH for this process.")

    # Step 4: Verify octo is callable
    print("Verifying Octopus CLI install with 'octo help'...")
    run_cmd("octo help")


===========================================================

curl -L -o OctopusTools.zip -H "User-Agent: Mozilla/5.0" ^
"https://download.octopusdeploy.com/octopus-tools/OctopusTools.8.4.0-win-x64.zip"


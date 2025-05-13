import os
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import requests
import zipfile
from dotenv import load_dotenv

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
    octo_url = "https://download.octopusdeploy.com/octopus-tools/OctopusTools.8.4.0-win-x64.zip"
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

def package_app(version):
    print("\n📦 Packaging app with Octopus CLI...")
    command = (
        f'octo pack --id="TestApp" '
        f'--format="Zip" '
        f'--version="{version}" '
        f'--basePath="artifacts/TestApp" '
        f'--outFolder="artifacts"'
    )
    run_cmd(command)

def push_package(version):
    print("\n📤 Pushing package to Octopus Deploy...")
    api_key = os.getenv("OCTOPUSSERVERAPIKEY")
    server = os.getenv("OCTOPUSSERVERURL")
    space = os.getenv("OCTOPUSSERVER_SPACE")
    package_path = f"artifacts/TestApp.{version}.zip"

    command = (
        f'octo push --server="{server}" '
        f'--apiKey="{api_key}" '
        f'--space="{space}" '
        f'--package="{package_path}" '
        f'--overwrite-mode=OverwriteExisting'
    )
    run_cmd(command)

def create_release(version):
    print("\n🚀 Creating Octopus release...")
    command = (
        f'octo create-release --project="TestProject" '
        f'--version="{version}" '
        f'--server="{os.environ["OCTOPUSSERVERURL"]}" '
        f'--apiKey="{os.environ["OCTOPUSSERVERAPIKEY"]}" '
        f'--space="{os.environ["OCTOPUSSERVER_SPACE"]}"'
    )
    run_cmd(command)

def deploy_release(version):
    print("\n🚀 Deploying release to 'Test' environment...")
    command = (
        f'octo deploy-release --project="TestProject" '
        f'--version="{version}" '
        f'--server="{os.environ["OCTOPUSSERVERURL"]}" '
        f'--apiKey="{os.environ["OCTOPUSSERVERAPIKEY"]}" '
        f'--space="{os.environ["OCTOPUSSERVER_SPACE"]}" '
        f'--deployTo="Test"'
    )
    run_cmd(command)

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
        package_app(version)
        push_package(version)
        create_release(version)
        deploy_release(version)

    elif args.test:
        print("\n[MODE] Test mode (--test)")
        install_dependencies()
        run_tests()

    elif args.package:
        print("\n[MODE] Package mode (--package)")
        create_artifacts_folder()
        copy_app_files()
        install_octopus_cli()
        package_app(version)

    elif args.deploy_only:
        print("\n[MODE] Deploy-only mode (--deploy-only)")
        push_package(version)
        create_release(version)
        deploy_release(version)

    else:
        print("\n[ERROR] No valid option provided.")
        parser.print_help()

    print("\n=== ✅ Script Completed ===")

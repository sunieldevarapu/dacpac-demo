import os
import subprocess
import shutil
from datetime import datetime

def run_cmd(command, shell=True, check=True):
    print(f"Running: {command}")
    subprocess.run(command, shell=shell, check=check)

def set_version():
    version = datetime.now().strftime("%Y.%m.%d") + f".{os.getenv('GITHUB_RUN_NUMBER', '1')}"
    os.environ["PACKAGE_VERSION"] = version
    print(f"Set PACKAGE_VERSION: {version}")
    return version

def install_dependencies():
    run_cmd("python -m pip install --upgrade pip")
    run_cmd("pip install -r requirements.txt")

def run_tests():
    run_cmd("python -m unittest discover -s tests")

def create_artifacts_folder():
    os.makedirs("artifacts/TestApp", exist_ok=True)
    print("Created artifacts/TestApp directory")

def copy_app_files():
    src_dir = "test_app"
    dest_dir = "artifacts/TestApp"
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        print(f"Copied contents of {src_dir} to {dest_dir}")
    else:
        print(f"Source directory '{src_dir}' does not exist.")

def install_octopus_cli():
    run_cmd("dotnet tool install --global OctopusTools")

def package_app(version):
    run_cmd(
        f'octo pack --id="TestApp" '
        f'--format="Zip" '
        f'--version="{version}" '
        f'--basePath="artifacts/TestApp" '
        f'--outFolder="artifacts"'
    )

def push_package(version):
    api_key = os.environ["OCTOPUSSERVERAPIKEY"]
    server = os.environ["OCTOPUSSERVERURL"]
    space = os.environ["OCTOPUSSERVER_SPACE"]
    package_path = f"artifacts/TestApp.{version}.zip"

    run_cmd(
        f'octo push --server="{server}" '
        f'--apiKey="{api_key}" '
        f'--space="{space}" '
        f'--package="{package_path}" '
        f'--overwrite-mode=OverwriteExisting'
    )

def create_release(version):
    run_cmd(
        f'octo create-release --project="TestProject" '
        f'--version="{version}" '
        f'--server="{os.environ["OCTOPUSSERVERURL"]}" '
        f'--apiKey="{os.environ["OCTOPUSSERVERAPIKEY"]}" '
        f'--space="{os.environ["OCTOPUSSERVER_SPACE"]}"'
    )

def deploy_release(version):
    run_cmd(
        f'octo deploy-release --project="TestProject" '
        f'--version="{version}" '
        f'--server="{os.environ["OCTOPUSSERVERURL"]}" '
        f'--apiKey="{os.environ["OCTOPUSSERVERAPIKEY"]}" '
        f'--space="{os.environ["OCTOPUSSERVER_SPACE"]}" '
        f'--deployTo="Test"'
    )

if __name__ == "__main__":
    version = set_version()
    install_dependencies()
    run_tests()
    create_artifacts_folder()
    copy_app_files()
    install_octopus_cli()
    package_app(version)
    push_package(version)
    create_release(version)
    deploy_release(version)

# export OCTOPUSSERVERAPIKEY=your_api_key
# export OCTOPUSSERVERURL=https://your.octopus.server
# export OCTOPUSSERVER_SPACE=your_space_name
# export GITHUB_RUN_NUMBER=123

import json
import urllib.parse
import requests
import re
import os
import logging
from requests.auth import HTTPBasicAuth
from logwrite import log

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def log(message):
    """Log messages to stdout"""
    logger.info(message)

# Load configuration from environment with fallback for dev (optional)
scheduler_config = {
    'BaseUrl': os.environ.get('SNOW_BASE_URL', 'https://your-instance.service-now.com'),
    'QueryChangeTaskEndpoint': os.environ.get('SNOW_QUERY_CHANGE_TASK_ENDPOINT', '/api/now/table/change_task'),
    'UpdateChangeTaskEndpoint': os.environ.get('SNOW_UPDATE_CHANGE_TASK_ENDPOINT', '/api/now/table/change_task'),
    'ApiAuthentication': {
        'Username': os.environ.get('SNOW_USERNAME', 'AUTOOCTOPUS'),
        'Password': os.environ.get('SNOW_PASSWORD', '@ut00ct0pu$')
    },
    'AutomationUserId': os.environ.get('SNOW_AUTOMATION_USER_ID', 'your-automation-user-id'),
    'ChsDevOpsSoftwareSolutionsId': os.environ.get('SNOW_DEV_OPS_SOFTWARE_SOLUTIONS_ID', 'your-group-id')
}

def validate_config():
    missing = []
    if not scheduler_config['BaseUrl']:
        missing.append("SNOW_BASE_URL")
    if not scheduler_config['ApiAuthentication'].get("Username"):
        missing.append("SNOW_USERNAME")
    if not scheduler_config['ApiAuthentication'].get("Password"):
        missing.append("SNOW_PASSWORD")
    if not scheduler_config['AutomationUserId']:
        missing.append("SNOW_AUTOMATION_USER_ID")
    if not scheduler_config['ChsDevOpsSoftwareSolutionsId']:
        missing.append("SNOW_DEV_OPS_SOFTWARE_SOLUTIONS_ID")
    if missing:
        raise Exception(f"Missing required environment variables: {', '.join(missing)}")

validate_config()

def retrieve_snow_items(endpoint: str, query_string: str) -> list:
    """Gets SNOW items from specified endpoint"""
    url = f"{scheduler_config['BaseUrl']}{endpoint}{query_string}"
    log(f"[INFO] Calling URL: {url}")
    log(f"[INFO] Using username: {scheduler_config['ApiAuthentication']['Username']}")

    headers = {"Accept": "application/json"}

    try:
        response = requests.get(
            url=url,
            auth=HTTPBasicAuth(
                scheduler_config["ApiAuthentication"]["Username"],
                scheduler_config["ApiAuthentication"]["Password"]
            ),
            headers=headers
        )
    except Exception as e:
        log(f"[ERROR] Request failed: {str(e)}")
        return []

    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        log(f"[ERROR] Status {response.status_code} - {response.text}")
        return []

def query_builder(assigned_to: bool) -> str:
    query = []
    query.append(f"assigned_to={scheduler_config['AutomationUserId']}") if assigned_to else query.append("assigned_toISEMPTY")
    query.append("active=true")
    query.append(f"assignment_group={scheduler_config['ChsDevOpsSoftwareSolutionsId']}")
    query.append("planned_start_dateISNOTEMPTY")
    query.append("planned_end_dateISNOTEMPTY")

    query_string = "^".join(query)
    return urllib.parse.quote(query_string)

def change_tasks(assigned_to: bool) -> list:
    change_tasks = retrieve_snow_items(
        endpoint=scheduler_config["QueryChangeTaskEndpoint"],
        query_string=query_builder(assigned_to=assigned_to)
    )

    return [
        task for task in change_tasks
        if "IGNORE" not in str(task.get("short_description", "")).upper()
    ]

def is_a_standard_change(short_description: str, parent_link: str) -> bool:
    chg_record = retrieve_parent_change(parent_link)
    return bool(
        re.search(r"(ssis)", short_description, re.IGNORECASE) and chg_record.get("type") == "standard"
    )

def retrieve_parent_change(parent_link: str) -> dict:
    headers = {"Accept": "application/json"}
    try:
        log(f"[INFO] Retrieving parent change from: {parent_link}")
        response = requests.get(
            url=parent_link,
            auth=HTTPBasicAuth(
                scheduler_config["ApiAuthentication"]["Username"],
                scheduler_config["ApiAuthentication"]["Password"]
            ),
            headers=headers
        )
        if response.status_code == 200:
            return response.json().get("result", {})
        else:
            log(f"[ERROR] Failed to retrieve parent change: {response.text}")
    except Exception as e:
        log(f"[ERROR] Exception retrieving parent change: {str(e)}")

    return {}

def set_processed(short_description: str, assign_to_queue: bool, parent_link: str) -> str:
    if not is_a_standard_change(short_description, parent_link):
        if assign_to_queue:
            return short_description.replace("PROCESSED", "").rstrip()
        else:
            return f"{short_description.replace('PROCESSED','').rstrip()} PROCESSED"
    return short_description

def assign_snow_item(snow_item: dict, assign_to_queue: bool) -> bool:
    headers = {"Accept": "application/json"}
    body = {
        "change_task_type": "Planning" if assign_to_queue else "Implementation",
        "state": "Open" if assign_to_queue else "Ready",
        "assigned_to": "" if assign_to_queue else scheduler_config["AutomationUserId"],
        "short_description": set_processed(
            snow_item["short_description"],
            assign_to_queue,
            snow_item["change_request"]["link"]
        )
    }

    if is_a_standard_change(snow_item["short_description"], snow_item["change_request"]["link"]):
        body.pop("short_description")

    url = f"{scheduler_config['BaseUrl']}{scheduler_config['UpdateChangeTaskEndpoint']}/{snow_item['sys_id']}"
    log(f"[INFO] Updating SNOW item at URL: {url}")

    try:
        response = requests.put(
            url=url,
            auth=HTTPBasicAuth(
                scheduler_config["ApiAuthentication"]["Username"],
                scheduler_config["ApiAuthentication"]["Password"]
            ),
            headers=headers,
            data=json.dumps(body)
        )
        if response.status_code == 200:
            return True
        else:
            log(f"[ERROR] Update failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log(f"[ERROR] Exception during update: {str(e)}")
        return False

def unassign(snow_items: list) -> None:
    if snow_items:
        for item in snow_items:
            if "PROCESSED" not in item["short_description"] and not is_a_standard_change(item["short_description"], item["change_request"]["link"]):
                assign_snow_item(item, assign_to_queue=True)

def action_item(snow_item: str) -> bool:
    if snow_item:
        snow_item = snow_item.upper()
        if "IGNORE" in snow_item:
            return False
        for k in ["DEPLOY", "RELEASE", "MANUAL", "SKIP"]:
            if k in snow_item:
                return True
    return False

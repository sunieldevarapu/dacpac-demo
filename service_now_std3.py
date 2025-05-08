import json
import urllib.parse
import requests
import re
import os
import logging

# Setup logging for GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def log(message):
    """Log messages to stdout for GitHub Actions logs"""
    logger.info(message)
    print(f"[Log]: {message}")

# Hard-coded values for testing
url = 'https://your-instance.service-now.com'
username = 'your_username'
password = 'your_password'

scheduler_config = {
    'BaseUrl': 'https://your-instance.service-now.com',
    'QueryChangeTaskEndpoint': '/api/now/table/change_task',
    'UpdateChangeTaskEndpoint': '/api/now/table/change_task',
    'ApiAuthentication': {
        'Username': 'your_username',
        'Password': 'your_password'
    },
    'AutomationUserId': 'your_automation_user_id',
    'ChsDevOpsSoftwareSolutionsId': 'your_dev_ops_software_solutions_id'
}

print("Scheduler Config", scheduler_config)

def unassign(snow_items: list) -> None:
    print("unassign function called")
    try:
        if snow_items:
            for snow_item in snow_items:
                if ("PROCESSED" not in snow_item["short_description"]) and (
                    is_a_standard_change(snow_item["short_description"], snow_item["change_request"]["link"]) == False
                ):
                    assign_snow_item(snow_item=snow_item, assign_to_queue=True)
            print("snow_list", snow_items)
    except Exception as e:
        log(f"Exception in unassign: {e}")

def action_item(snow_item: str) -> bool:
    if snow_item:
        snow_item = snow_item.upper()
        print("snow_item", snow_item)
        if "IGNORE" in snow_item:
            return False
        keywords = ["DEPLOY", "RELEASE", "MANUAL", "SKIP"]
        for k in keywords:
            if k in snow_item:
                return True
        return False

def retrieve_snow_items(endpoint: str, query_string: str) -> list:
    try:
        results = requests.get(
            url=f"{scheduler_config['BaseUrl']}{endpoint}{query_string}",
            auth=(
                scheduler_config["ApiAuthentication"]["Username"],
                scheduler_config["ApiAuthentication"]["Password"],
            ),
        )
    except Exception as e:
        error_string = str(e)
        log(error_string)
        return []
    if results.status_code == 200:
        results = results.json()
        print("results", results)
        return results["result"]
    else:
        log(results.text)
        return []

def query_builder(assigned_to: bool) -> str:
    query = []
    query.append(
        f"assigned_to={scheduler_config['AutomationUserId']}"
    ) if assigned_to else query.append("assigned_toISEMPTY")
    query.append("active=true")
    query.append(f"assignment_group={scheduler_config['ChsDevOpsSoftwareSolutionsId']}")
    query.append("planned_start_dateISNOTEMPTY")
    query.append("planned_end_dateISNOTEMPTY")
    query_to_string = ""
    for q in query:
        query_to_string += f"{q}^"
    print("Query String", query_to_string)
    return urllib.parse.quote(query_to_string.rstrip(query_to_string[-1]))

def change_tasks(assigned_to: bool) -> list:
    change_tasks = retrieve_snow_items(
        endpoint=scheduler_config["QueryChangeTaskEndpoint"],
        query_string=query_builder(assigned_to=assigned_to),
    )
    mod_changed_tasks = []
    [
        mod_changed_tasks.append(task)
        for task in change_tasks
        if "IGNORE" not in str(task["short_description"]).upper()
    ]
    return mod_changed_tasks

def set_processed(short_description: str, assign_to_queue: bool, parent_link: str) -> str:
    if is_a_standard_change(short_description, parent_link) == False:
        if assign_to_queue:
            return short_description.replace(
                "PROCESSED", ""
            ).rstrip()
        else:
            return f"{short_description.replace('PROCESSED','').rstrip()} PROCESSED"

def assign_snow_item(snow_item: dict, assign_to_queue: bool) -> bool:
    json_body = {
        "change_task_type": "Planning"
        if assign_to_queue
        else "Implementation",
        "state": "Open"
        if assign_to_queue
        else "Ready",
        "assigned_to": "" if assign_to_queue else scheduler_config["AutomationUserId"],
        "short_description": set_processed(
            short_description=snow_item["short_description"],
            assign_to_queue=assign_to_queue,
            parent_link=snow_item["change_request"]["link"],
        ),
    }
    endpoint = scheduler_config["UpdateChangeTaskEndpoint"]
    if is_a_standard_change(snow_item["short_description"], snow_item["change_request"]["link"]):
        json_body.pop("short_description")
    try:
        results = requests.put(
            url=f"{scheduler_config['BaseUrl']}{endpoint}/{snow_item['sys_id']}",
            auth=(
                scheduler_config["ApiAuthentication"]["Username"],
                scheduler_config["ApiAuthentication"]["Password"],
            ),
            data=json.dumps(json_body),
        )
    except Exception as e:
        log(e.message)
        return False
    if results.status_code != 200:
        log(results.text)
        return False
    else:
        return True

def is_a_standard_change(short_description: str, parent_link: str) -> bool:
    found = False
    chg_record = retrieve_parent_change(parent_link)
    if re.search(r"(ssis)", short_description, re.IGNORECASE):
        if chg_record["type"] == "standard":
            found = True
    return found

def retrieve_parent_change(parent_link: str) -> list:
    try:
        change = requests.get(
            url=f"{parent_link}",
            auth=(
                scheduler_config["ApiAuthentication"]["Username"],
                scheduler_config["ApiAuthentication"]["Password"],
            ),
        )
    except Exception as e:
        error_string = str(e)
        log(error_string)
        return []
    if change.status_code == 200:
        change = change.json()
        return change["result"]
    else:
        log(change.text)
        return []

if __name__ == "__main__":
    # Example data for testing
    snow_items = [
        {
            "short_description": "Test Change Task",
            "change_request": {"link": "https://your-instance.service-now.com/api/now/table/change_request/sys_id"},
            "sys_id": "example_sys_id"
        }
    ]
    
    # Call unassign function
    unassign(snow_items)
    
    # Call action_item function
    print(action_item("Deploy new version"))
    
    # Call retrieve_snow_items function
    print(retrieve_snow_items('/api/now/table/change_task', '?sys_id=example_sys_id'))
    
    # Call query_builder function
    print(query_builder(True))
    
    # Call change_tasks function
    print(change_tasks(True))
    
    # Call set_processed function
    print(set_processed("Test Change Task", True, "https://your-instance.service-now.com/api/now/table/change_request/sys_id"))
    
    # Call assign_snow_item function
    print(assign_snow_item(snow_items[0], True))
    
    # Call is_a_standard_change function
    print(is_a_standard_change("Test Change Task", "https://your-instance.service-now.com/api/now/table/change_request/sys_id"))
    
    # Call retrieve_parent_change function
    print(retrieve_parent_change("https://your-instance.service-now.com/api/now/table/change_request/sys_id"))

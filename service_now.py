import json
import urllib.parse
from cmadevops_deployment_scheduler.config.config import scheduler_config
import requests
import re
from cmadevops_deployment_scheduler.modules.logwrite import log


def unassign(snow_items: list) -> None:
    """Unassigns a task that has been assigned to the automation account

    Keyword arguments:
    snow_items -- list of ServiceNow items
    Return: none
    """

    # we need to verify that a task that has been assigned has actually been scheduled
    # if it has been assigned and not scheduled it needs to be assigned back to the queue so it can be picked up and scheduled on the next run
    if snow_items:
        for snow_item in snow_items:
            if ("PROCESSED" not in snow_item["short_description"]) and (
                is_a_standard_change(snow_item["short_description"], snow_item["change_request"]["link"]) == False
            ):
                assign_snow_item(snow_item=snow_item, assign_to_queue=True)


def action_item(snow_item: str) -> bool:
    """
    Find any item from ServiceNow that contains Deploy, Release, Manual, or Skip
        Parameters:
            snow_item: response from ServiceNow
    """

    if snow_item:
        # capitalize string
        snow_item = snow_item.upper()

        # if "IGNORE" keyword is found return false
        if "IGNORE" in snow_item:
            return False

        # keywords that defines an action item
        keywords = ["DEPLOY", "RELEASE", "MANUAL", "SKIP"]

        # find keyword
        for k in keywords:
            if k in snow_item:
                return True

    # if this is reached no keyword was found
    return False


def retrieve_snow_items(endpoint: str, query_string: str) -> list:
    """
    Gets SNOW items from specified endpoint
        Parameters:
            endpoint: ServiceNow API endpoint
            query_string: query to return records from ServiceNOw
    """

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
        return results["result"]
    else:
        log(results.text)
        return []


def query_builder(assigned_to: bool) -> str:
    """
    Builds query string for querying all unassigned or assigned Change Tasks in ServiceNow
        Parameters:
            assigned_to: Builds querystring for tasks that are assigned to automation account or query for unassigned tasks
    """

    query = []
    query.append(
        f"assigned_to={scheduler_config['AutomationUserId']}"
    ) if assigned_to else query.append("assigned_toISEMPTY")
    query.append("active=true")
    query.append(f"assignment_group={scheduler_config['ChsDevOpsSoftwareSolutionsId']}")
    query.append("planned_start_dateISNOTEMPTY")
    query.append("planned_end_dateISNOTEMPTY")

    # convert the query list to a string
    query_to_string = ""
    for q in query:
        query_to_string += f"{q}^"

    # return the url parsed string and remove last ^ from string as we dont need it
    return urllib.parse.quote(query_to_string.rstrip(query_to_string[-1]))


def change_tasks(assigned_to: bool) -> list:
    """
    Gets all unassigned or assigned change tasks in ServiceNow assigned to the group identifier in config
        Parameters:
            assigned_to: Query for tasks that are assigned to automation account or query for unassigned tasks
    """

    # get all unassigned change tasks
    change_tasks = retrieve_snow_items(
        endpoint=scheduler_config["QueryChangeTaskEndpoint"],
        query_string=query_builder(assigned_to=assigned_to),
    )

    # return all unassigned change tasks that do not have the ignore keywoard
    mod_changed_tasks = []
    [
        mod_changed_tasks.append(task)
        for task in change_tasks
        if "IGNORE" not in str(task["short_description"]).upper()
    ]

    return mod_changed_tasks


def set_processed(short_description: str, assign_to_queue: bool, parent_link: str) -> str:
    """Injects PROCESSED to the end of the short desciption in ServiceNow"

    Keyword arguments:
    short_description -- short description in ServiceNow
    assign_to_queue: bool
    Return: str
    """

    if is_a_standard_change(short_description, parent_link) == False:
        if assign_to_queue:
            # if its assigned to the queue we need to remove the PROCESSED from the title
            return short_description.replace(
                "PROCESSED", ""
            ).rstrip()  # we add rstrip to keep spaces from stacking in the string
        else:
            # if it is not assigned to the queue then we need to add PROCESSED to the string
            # we attempt to replace PROCESSED if it already exists to keep it from stacking in the string
            return f"{short_description.replace('PROCESSED','').rstrip()} PROCESSED"


def assign_snow_item(snow_item: dict, assign_to_queue: bool) -> bool:
    """
    Assigns ServiceNow item to service account
        Parameters:
            snow_item: response from ServiceNow
            assign_to_queue: if true it assigns the snow item back to the queue
    """
    # we need to update the change task body
    json_body = {
        "change_task_type": "Planning"
        if assign_to_queue
        else "Implementation",  # change not whatever this needs to be
        "state": "Open"
        if assign_to_queue
        else "Ready",  # change to not ready when assigning back to queue
        "assigned_to": "" if assign_to_queue else scheduler_config["AutomationUserId"],
        "short_description": set_processed(
            short_description=snow_item["short_description"],
            assign_to_queue=assign_to_queue,
            parent_link=snow_item["change_request"]["link"],
        ),
    }
    endpoint = scheduler_config["UpdateChangeTaskEndpoint"]

    # You cannot update descriptions in task from standard changes
    # So we need to figure out if it is a standard change
    if is_a_standard_change(snow_item["short_description"], snow_item["change_request"]["link"]):
        json_body.pop("short_description")

    # update SNOW item
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

    # if the status code is not 200 then it failed
    if results.status_code != 200:
        log(results.text)
        return False
    else:
        return True
    
def is_a_standard_change(short_description: str, parent_link: str) -> bool:
    """Verifies if a project is a standard change
        by checking the short description for SSIS and that the parent change is a type=standard
    Args:
        short_description (str): Short description from ServiceNow
        parent_link (srt): comes from change_request.link in CTASK json

    Returns:
        bool: true or false
    """
    found = False
    chg_record = retrieve_parent_change(parent_link)
    if re.search(r"(ssis)", short_description, re.IGNORECASE):
        if chg_record["type"] == "standard":
            found = True

    return found

def retrieve_parent_change(parent_link: str) -> list:
    """
    Gets parent change from link in CTASK 
        Parameters:
            parent_link: change_request.link in CTASK json
    """

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

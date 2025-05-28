import os
import sys
import re
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone, tzinfo
import pytz
from pytz import BaseTzInfo, utc
from typing import Any, ClassVar, Mapping

# ---- Logging ----
def log(message):
    print(f"[LOG] {message}")

# ---- Config ----
scheduler_config = {}

if os.getenv("ASPNETCORE_ENVIRONMENT") == "Development":
    scheduler_config.update({
        "BaseUrl": "https://zilvertondev.service-now.com",
        "QueryChangeTaskEndpoint": "/api/now/table/change_task?sysparm_query=",
        "UpdateChangeTaskEndpoint": "/api/now/table/change_task",
        "ChsDevOpsSoftwareSolutionsId": "2daabc1ddbebb3002bded487f49619f0",
        "AutomationUserId": "196675b6db544c90b47d54f9489619da",
        "OctopusDeployApiKey": "API-TF21J6OCQK1HONXEQ95BYJWZJLTMETKB",
        "ReleaseEndpoint": "/api/releases",
        "TasksEndpoint": "/api/tasks",
        "DeploymentsEndpoint": "/api/deployments",
        "ProjectsEndpoint": "/api/projects",
        "OctopusDeployBaseUrl": "https://octopusdeploydev.silver.com",
        "ApiAuthentication": {"Username": "AUTOOCTOPUS", "Password": "@ut00ct0pu$"},
        "ProductionEnvironmentId": "Environments-14",
        "WebexUrl": "https://webexapis.com/v1/messages",
        "WebexRoom": "703b8fb0-15f0-11ee-b55b-2f8ddf8a82f4",
        "Bearer": "MzVhMzhlZWQtNTVjYS00YWI1LThlODQtNTg4YjY2NWIyMDE4M2VmMTBlZDEtMmIz_PF84_c2314722-4c4b-4b56-b3a3-eb0948e14363"
    })
elif os.getenv("ASPNETCORE_ENVIRONMENT") == "Production":
    scheduler_config.update({
        "BaseUrl": "https://zilvertondev.service-now.com",
        "QueryChangeTaskEndpoint": "/api/now/table/change_task?sysparm_query=",
        "UpdateChangeTaskEndpoint": "/api/now/table/change_task",
        "ChsDevOpsSoftwareSolutionsId": "2daabc1ddbebb3002bded487f49619f0",
        "AutomationUserId": "5e80a49c1bad98d058a1777e0a4bcb73",
        "OctopusDeployApiKey": "API-SHBCKLJIIXTYLMBGUSDS74UXVW",
        "ReleaseEndpoint": "/api/releases",
        "TasksEndpoint": "/api/tasks",
        "DeploymentsEndpoint": "/api/deployments",
        "ProjectsEndpoint": "/api/projects",
        "OctopusDeployBaseUrl": "https://octopusdeploy.sys.cigna.com",
        "ProductionEnvironmentId": "Environments-145",
        "ApiAuthentication": {"Username": "P-AUTOOCTOPUS", "Password": "7hxW%A%#5JPy"},
        "WebexUrl": "https://webexapis.com/v1/messages",
        "WebexRoom": "91486ae0-544d-11ec-ab7c-c903b8781690",
        "Bearer": "MzVhMzhlZWQtNTVjYS00YWI1LThlODQtNTg4YjY2NWIyMDE4M2VmMTBlZDEtMmIz_PF84_c2314722-4c4b-4b56-b3a3-eb0948e14363"
    })
else:
    raise Exception("ASPNETCORE_ENVIRONMENT must be set to Development or Production")

def log(message):
    print(f"[LOG] {message}")

def capture_output_to_file(filename):
    class Logger(object):
        def __init__(self):
            self.terminal = sys.stdout
            self.log = open(filename, "a")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass

    sys.stdout = Logger()

class _FixedOffset(tzinfo):
    zone: ClassVar[None]

    def __init__(self, minutes: int) -> None:
        self.__offset = timedelta(minutes=minutes)
        self.__name = f"{minutes:+03d}00"

    def utcoffset(self, dt: Any) -> timedelta:
        return self.__offset

    def dst(self, dt: Any) -> timedelta:
        return timedelta(0)

    def tzname(self, dt: Any) -> str:
        return self.__name

    def localize(self, dt: datetime, is_dst: bool = False) -> datetime:
        return dt.replace(tzinfo=self)

    def normalize(self, dt: datetime, is_dst: bool = False) -> datetime:
        return dt


# Actually named UTC and then masked with a singleton with the same name
class _UTCclass(BaseTzInfo):
    def localize(self, dt: datetime, is_dst: bool | None = False) -> datetime: ...
    def normalize(self, dt: datetime, is_dst: bool | None = False) -> datetime: ...
    def tzname(self, dt: datetime | None) -> str: ...
    def utcoffset(self, dt: datetime | None) -> timedelta: ...
    def dst(self, dt: datetime | None) -> timedelta: ...

utc: _UTCclass
UTC: _UTCclass

#def timezone(zone: str) -> _UTCclass | StaticTzInfo | DstTzInfo: ...

# class _FixedOffset(datetime.tzinfo):
#     zone: ClassVar[None]
#     def __init__(self, minutes: int) -> None: ...
#     def utcoffset(self, dt: Any) -> timedelta | None: ...
#     def dst(self, dt: Any) -> timedelta: ...
#     def tzname(self, dt: Any) -> None: ...
#     def localize(self, dt: datetime, is_dst: bool | None = False) -> datetime: ...
#     def normalize(self, dt: datetime, is_dst: bool | None = False) -> datetime: ...

def FixedOffset(offset: int, _tzinfos: dict[int, _FixedOffset] = {}) -> _UTCclass | _FixedOffset: ...

all_timezones: list[str]
all_timezones_set: set[str]
common_timezones: list[str]
common_timezones_set: set[str]
country_timezones: Mapping[str, list[str]]
country_names: Mapping[str, str]
ZERO: timedelta
HOUR: timedelta
VERSION: str

__all__ = [
    "timezone",
    "utc",
    "country_timezones",
    "country_names",
    "AmbiguousTimeError",
    "InvalidTimeError",
    "NonExistentTimeError",
    "UnknownTimeZoneError",
    "all_timezones",
    "all_timezones_set",
    "common_timezones",
    "common_timezones_set",
    "BaseTzInfo",
    "FixedOffset",
]


# Base configuration
INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "https://service-now.com")
USERNAME = os.getenv("SERVICENOW_USERNAME", "")
PASSWORD = os.getenv("SERVICENOW_PASSWORD", "")

def get_servicenow_data(endpoint, params=None):
    """
    Makes a GET request to the ServiceNow API using basic authentication.
    """
    url = f"{INSTANCE_URL}{endpoint}"
    headers = {"Accept": "application/json"}
    print(f"[INFO] Requesting URL: {url}")
    if params:
        print(f"[INFO] With parameters: {params}")
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, params=params)
        response.raise_for_status()
        print("[SUCCESS] Data retrieved successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return {"error": str(e)}

def get_unassigned_tasks():
    """
    Retrieves unassigned tasks from the ServiceNow task table.
    """
    print("\n[INFO] Fetching unassigned tasks...")
    endpoint = "/api/now/table/change_task?sysparm_query="
    params = {
        "sysparm_query": "assigned_toISEMPTY",
        "sysparm_limit": "10"
    }
    return get_servicenow_data(endpoint, params)

def get_change_tasks():
    """
    Retrieves change tasks from the ServiceNow change_task table.
    """
    print("\n[INFO] Fetching change tasks...")
    endpoint = "/api/now/table/change_task"
    params = {
        "sysparm_limit": "10"
    }
    return get_servicenow_data(endpoint, params)

def convert_utc_offset(date_string: str):
    """
    Converts UTC offset to Central Time
    Parameters:
    date_string: datetime string to be converted to central time
    """
    if not date_string or not date_string.strip():
        return "Invalid Date"
    try:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M")
    except ValueError as e:
        print(f"[ERROR] Date parsing failed: {e}")
        return "Invalid Date"

def to_central_time(time=str, add_delta=bool) -> str:
    """
    Converts UTC to CST from ServiceNow for Octopus Deploy
        Parameters:
            time: YYYY-MM-DD HH:MM:SS
            add_delta: If set to true it adds 30 minutes for the deployment expirey time
    """
    try:
        utc_time = utc.localize(datetime.strptime(time, "%Y-%m-%d %H:%M:%S"))
    except:
        return ""

    if add_delta:
        utc_time = utc.localize(
            datetime.strptime(time, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=30)
        )

    cst_time = timezone("US/Central")
    return utc_time.astimezone(cst_time).isoformat()

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
    
def post_to_webex(message=str):
    """Posts message to webex space"""
    try:
        payload = {"roomId": scheduler_config["WebexRoom"], "markdown": message}        
        headers = {"Authorization": "Bearer " f'{scheduler_config["Bearer"]}'}

        requests.post(scheduler_config["WebexUrl"], headers=headers, data=payload).json()
        return True
    except Exception as e:
        error_string = str(e)
        log(error_string)
        return False
    
def remove_project_name(short_description=str) -> str:
    """Removes project name from short description

    Args:
        short_description (_type_, optional): SNOW short description. Defaults to str.

    Returns:
        str: returns short description with project name removed
    """
    try:
        od_projects = projects()
    except:
        return ""

    for project in od_projects:
        if (
            re.search(
                r"\b{}\b".format(str(project["Name"])), short_description, re.IGNORECASE
            )
            is not None
        ):
            short_description = short_description.replace(project["Name"], "")
            break
    return short_description
    
def extract_release(short_description: str) -> str:
    """
    Extracts release from description in ServiceNow
        Parameters:
            short_description: short description of Change Task in ServiceNow

    """
    # to avoid extracting project names as version numbers due to some projects having numbers in their names
    # we find the project name in the description and remove it as we just want the version number
    short_description = remove_project_name(short_description=short_description)

    # use regex to find version number in the short description
    release_number = ""
    matches = re.findall(r"\d*\.?\d+[-]?[-a-zA-Z]*", short_description)

    # its possible the regex will return more than match so we need to combine them for the whole release number
    if matches:
        for match in matches:
            release_number += match

    # return extracted release number
    return release_number

def find_project_id(short_description: str) -> str:
    """
    Finds project id in OctopusDeploy from the ServiceNow description
    Parameters:
        short_description: short description of Change Task in ServiceNow
    """

    # TODO improvement: convert project name in short_description to slug, pass slug to projects() function

    # get list of projects from OD return empty string if there is an error
    try:
        od_projects = projects()
    except:
        return ""

    # if there are no OD projects something went wrong so just return an empty string
    if not od_projects:
        return ""

    # all upper case to avoid cAsE problems
    short_description = short_description.upper()

    # we want to make sure that the paramters were passed in
    if short_description:
        # look for the project name in the ServiceNow short description
        for project in od_projects:
            if str(project["Name"]).upper() in short_description:
                return project["Id"]

        return ""
    else:
        return ""
    
def find_release(release_number: str, project_id: str) -> dict:
    """
    Finds release in Octopus Deploy
    Parameters:
        release_number: release number in Octopus Deploy
        project_id: id of project in Octopus Deploy
    """
    # TODO can't seem to pass slug as project id for releases (https://octopusdeploy.healthspring.inside/api/projects/Projects-644/releases)
    # TODO do we really need 999 releases?  Defaults to last 30 and returns most recent first
    # TODO we can request specific release based on version number (https://octopusdeploy.healthspring.inside/api/projects/Projects-644/releases/2023.4.0.246)
    if release_number and project_id:
        try:
            # retrieve 999 releases we may need to extend the number in the future, but for now should be plenty
            results = requests.get(
                url=f"{scheduler_config['OctopusDeployBaseUrl']}{scheduler_config['ProjectsEndpoint']}/{project_id}/releases?take=999",
                headers={
                    "X-Octopus-ApiKey": f"{scheduler_config['OctopusDeployApiKey']}"
                },
                verify=False,
            )
        except Exception as e:
            error_string = str(e)
            log(error_string)
            return {}

        # if status code is 200 then content was returned
        if results.status_code == 200:
            results = results.json()

            # results we want are in the Items list
            for r in results["Items"]:
                # Version should equal the release number passed in
                if r["Version"].upper() == release_number.upper():
                    return r
            return {}
    else:
        return {}
    
def scheduled(release_number: str, project_name=str) -> bool:
    """
    Verifies if a release is scheduled in Octopus Deploy
        Parameters:
            release_number: Release number from Octopus Deploy
    """

    # retrieve current server tasks
    if release_number:
        try:
            results = requests.get(
                url=f"{scheduler_config['OctopusDeployBaseUrl']}{scheduler_config['TasksEndpoint']}",
                headers={
                    "X-Octopus-ApiKey": f"{scheduler_config['OctopusDeployApiKey']}"
                },
                verify=False,
            )
        except Exception as e:
            error_string = str(e)
            log(error_string)
            return False

        # we only want to results if code is 200, otherwise return false
        if results.status_code == 200:
            results = results.json()

            # find release number in the description if it's found and the state is queued then
            # this release is already scheduled so return true
            for r in results["Items"]:
                if (
                    release_number == extract_release(r["Description"])
                    and r["State"] == "Queued"
                    and "Release Approval" not in r["Description"]
                    and project_name == find_project_name(r["Description"])
                ):
                    return True
        else:
            log(results.text)
    return False

def projects() -> list:
    """Gets a list of all projects from Octopus Deploy"""
    try:
        results = requests.get(
            url=f"{scheduler_config['OctopusDeployBaseUrl']}{scheduler_config['ProjectsEndpoint']}?take=999",
            headers={"X-Octopus-ApiKey": f"{scheduler_config['OctopusDeployApiKey']}"},
            verify=False,
        )
    except:
        return []

    # we only want results if the status code is 200
    if results.status_code == 200:
        results = results.json()
        return results["Items"]

    # return empty list if it is other than 200
    else:
        log(results.text)
        return []

def find_project_name(short_description=str) -> str:
    """Returns project name from short description

    Args:
        short_description (_type_, optional): SNOW short description. Defaults to str.

    Returns:
        str: returns project name
    """
    project_name = ""
    try:
        od_projects = projects()
    except:
        return project_name

    for project in od_projects:
        if (
            re.search(
                r"\b{}\b".format(str(project["Name"])), short_description, re.IGNORECASE
            )
            is not None
        ):
            project_name = project["Name"]
            break

    return project_name

def promotable(release_id: str) -> bool:
    """
    Verifies that a release is able to be promoted to selected environment in Octopus Deploy
        Parameters:
            release_id: ID of release
    """

    # get the release progression
    try:
        results = requests.get(
            url=f"{scheduler_config['OctopusDeployBaseUrl']}{scheduler_config['ReleaseEndpoint']}/{release_id}/progression",
            headers={"X-Octopus-ApiKey": f"{scheduler_config['OctopusDeployApiKey']}"},
            verify=False,
        )
    except:
        return False

    # we only want results if the code is 200, otherwise it means it failed
    if results.status_code == 200:
        results = results.json()

        # verify that the release can be promoted to Prod
        for r in results["Phases"]:
            if (
                r["Name"] != "Release Approval"
                and r["Name"] == "Prod"
                or r["Name"] == "Production"
                or r["Name"] == "Hotfix"
            ) and (
                r["Blocked"] == False
                and r["Progress"] == "Current"
                or r["Progress"] == "Complete"
            ):
                return True
        return False
    else:
        log(results.text)
        return False
    
scheduler_config = {}

# config for development environment
if os.getenv("ASPNETCORE_ENVIRONMENT") == "Development":
    scheduler_config.update(
        {
            "BaseUrl": "https://zilvertondev.service-now.com",
            "QueryChangeTaskEndpoint": "/api/now/table/change_task?sysparm_query=",
            "UpdateChangeTaskEndpoint": "/api/now/table/change_task",
            "ChsDevOpsSoftwareSolutionsId": "2daabc1ddbebb3002bded487f49619f0",
            "AutomationUserId": "196675b6db544c90b47d54f9489619da",
            "OctopusDeployApiKey": "API-TF21J6OCQK1HONXEQ95BYJWZJLTMETKB",
            "ReleaseEndpoint": "/api/releases",
            "TasksEndpoint": "/api/tasks",
            "DeploymentsEndpoint": "/api/deployments",
            "ProjectsEndpoint": "/api/projects",
            "OctopusDeployBaseUrl": "https://octopusdeploydev.silver.com",
            "ApiAuthentication": {"Username": "AUTOOCTOPUS", "Password": "@ut00ct0pu$"},
            "ProductionEnvironmentId": "Environments-14",
            "WebexUrl": "https://webexapis.com/v1/messages",
            "WebexRoom": "703b8fb0-15f0-11ee-b55b-2f8ddf8a82f4",
            "Bearer": "MzVhMzhlZWQtNTVjYS00YWI1LThlODQtNTg4YjY2NWIyMDE4M2VmMTBlZDEtMmIz_PF84_c2314722-4c4b-4b56-b3a3-eb0948e14363"
        }
    )

# config for production environment
elif os.getenv("ASPNETCORE_ENVIRONMENT") == "Production":
    scheduler_config.update(
        {
            "BaseUrl": "https://zilvertondev.service-now.com",
            "QueryChangeTaskEndpoint": "/api/now/table/change_task?sysparm_query=",
            "UpdateChangeTaskEndpoint": "/api/now/table/change_task",
            "ChsDevOpsSoftwareSolutionsId": "2daabc1ddbebb3002bded487f49619f0",
            "AutomationUserId": "5e80a49c1bad98d058a1777e0a4bcb73",
            "OctopusDeployApiKey": "API-SHBCKLJIIXTYLMBGUSDS74UXVW",
            "ReleaseEndpoint": "/api/releases",
            "TasksEndpoint": "/api/tasks",
            "DeploymentsEndpoint": "/api/deployments",
            "ProjectsEndpoint": "/api/projects",
            "OctopusDeployBaseUrl": "https://octopusdeploy.sys.cigna.com",
            "ProductionEnvironmentId": "Environments-145",
            "ApiAuthentication": {
                "Username": "P-AUTOOCTOPUS",
                "Password": "7hxW%A%#5JPy"},
            "WebexUrl" : "https://webexapis.com/v1/messages",
            "WebexRoom": "91486ae0-544d-11ec-ab7c-c903b8781690",
            "Bearer": "MzVhMzhlZWQtNTVjYS00YWI1LThlODQtNTg4YjY2NWIyMDE4M2VmMTBlZDEtMmIz_PF84_c2314722-4c4b-4b56-b3a3-eb0948e14363"
        }
    )
# raise exception if there is no system environment variable set
else:
    raise Exception(
        "Please very ASPNETCORE_ENVIRONMENT system environment variable is set to Development or Production."
    )

def schedule_release(deployment_resource: dict) -> bool:
    """
    Schedules release in Octopus Deploy
        Parameters:
            deployment_resource = {
                "ReleaseId": "Release-1",
                "ProjectId: "Project-1"
                "ChannelId" "Channel-1"
                "EnvironmentId":"Environment-123",
                "QueueTime": "YYYY-MM-DDTHH:MM:SS",
                "QueueTimeExpiry":"YYYY-MM-DDTHH:MM:SS"
            }
    """

    # verify that the deployment resource is not null
    if deployment_resource:
        results = requests.post(
            url=f"{scheduler_config['OctopusDeployBaseUrl']}{scheduler_config['DeploymentsEndpoint']}",
            headers={"X-Octopus-ApiKey": f"{scheduler_config['OctopusDeployApiKey']}"},
            json=deployment_resource,
            verify=False,
        )

        # if the result status code is not 201 then something failed
        if results.status_code == 201:
            return True
        else:
            log(results.status_code)
            results = results.json()
            # log(results["Errors"].text)
            return False
    else:
        return False

def schedule(snow_items=list) -> bool:
    """
    Assigns and schedules ServiceNow items in Octopus Deploy
        Parameters:
            snow_items: JSON response from ServiceNow
    """
    if snow_items:
        for snow_item in snow_items:
            # This string gets added to throughout the schedule function and posts to webex
            webex_message = ""

            # we need to convert the UTC offset that OD uses to CST
            # TODO - why are we not pulling the planned_end_time instead of just adding 30 minutes to start time?
            start_time = convert_utc_offset(
                date_string=to_central_time(
                    time=snow_item["planned_start_date"], add_delta=False
                )
            )
            end_time = convert_utc_offset(
                date_string=to_central_time(
                    time=snow_item["planned_start_date"], add_delta=True
                )
            )

            # set the snow item number, time, and description for the webex message
            webex_message = (
                f'ServiceNow Item: _{snow_item["task_effective_number"]}_ \n'
                f"Time: _{start_time} CST - {end_time} CST_ \n"
                f'Description: _{snow_item["short_description"]}_ \n'
            )

            # we only want to schedule items that apply to OD
            # TODO this could be simplified, perhaps return the action verb from action_item?
            if action_item(snow_item["short_description"]):
                # if skip is in the keyword we do not want schedule
                # convert description to all upper case to avoid any cAsE problems
                description_upper = str(snow_item["short_description"]).upper()

                if "SKIP" in description_upper:
                    if assign_snow_item(snow_item=snow_item, assign_to_queue=False):
                        webex_message += (
                            f"Status: **Found override keyword SKIP.** \n"
                            f"  - ServiceNow item has been assigned to P-AUTOCTOPUS. \n"
                            f"  - Deployment HAS NOT been scheduled in Octopus Deploy. Development team will manually trigger the deployment. \n"
                            f"_No further action needed._ \n"
                        )
                    else:
                        webex_message += "Status: ** - Failed to assign ServiceNow item to P-AUTOOCTOPUS.** \n"

                    post_to_webex(message=webex_message)
                    continue

                # if manual is in the keyword notify webex
                if "MANUAL" in description_upper:
                    webex_message += (
                        "Status: **Found override keyword MANUAL** \n"
                        "   - Please assign this ServiceNow item to whoever will be on call the week of the deployment or Production Support. \n"
                    )

                    post_to_webex(message=webex_message)
                    continue
                
                # assign snow item to autooctopus
                # TODO I think this needs to move later in the process to avoid the assign/unassign loop when there is an issue later in the process
                if not assign_snow_item(snow_item=snow_item, assign_to_queue=False):
                    webex_message += "Status: **Failed to assign ServiceNow item to P-AUTOCTOPUS.** \n"
                    post_to_webex(message=webex_message)
                    continue

                # extract the version number from the description
                release_number = extract_release(snow_item["short_description"])

                # we need to verify that the release number is not null
                if not release_number:
                    webex_message += (
                        "Status: **Unable to extract release from ServiceNow short description.** \n"
                        "_Possible Solutions:_ \n"
                        "   - Please ensure title is in following format: \n"
                        "Deploy [_project name_] [_release number_] [_override_] \n"
                    )
                    assign_snow_item(snow_item=snow_item, assign_to_queue=True) # TODO not necessary if we don't assign by default on line 83
                    post_to_webex(message=webex_message)
                    continue

                # get the project name and project id
                project_id = find_project_id(
                    short_description=snow_item["short_description"]
                )

                if not project_id:
                    webex_message += (
                        "Status: **Unable to find project in Octopus Deploy.** \n"
                        "_Possible Solutions:_ \n"
                        "   - Please verify that you have spelled your project name correctly in the title \n"
                    )
                    assign_snow_item(snow_item=snow_item, assign_to_queue=True) # TODO not necessary if we don't assign by default on line 83
                    post_to_webex(message=webex_message)
                    continue

                # find release in octopus deploy
                release_details = find_release(
                    release_number=release_number, project_id=project_id
                )

                if not release_details:
                    webex_message += (
                        f"Status: **The release number {release_number} was not found in Octopus Deploy!** \n"
                        "_Possible Solutions:_ \n"
                        "   - Please ensure that the release in the ServiceNow item matches what release is being deployed. \n"
                    )
                    assign_snow_item(snow_item=snow_item, assign_to_queue=True)
                    post_to_webex(message=webex_message)
                    continue

                # if release is not scheduled
                if not scheduled(
                    release_number=release_number,
                    project_name=find_project_name(snow_item["short_description"]),
                ):
                    # Verify that environment is able to be promoted to prod
                    if not promotable(release_id=str(release_details["Id"])):
                        # IF ITS NOT PROMOTABLE post message
                        webex_message += (
                            f"Status: **The release number {release_number} is unable to be promoted to Production!** \n"
                            "_Possible Solutions:_ \n"
                            "   - Please ensure that the release has gone through the lifecycle in Octopus Deploy to reach Production and is in the correct channel. \n"
                        )
                        assign_snow_item(snow_item=snow_item, assign_to_queue=True)
                        post_to_webex(message=webex_message)
                        continue

                    # deployment resource for octopus deploy to create deployment
                    deployment_resource = {
                        "ReleaseId": release_details["Id"],
                        "ProjectId": release_details["ProjectId"],
                        "ChannelId": release_details["ChannelId"],
                        "EnvironmentId": scheduler_config["ProductionEnvironmentId"],
                        "QueueTime": to_central_time(
                            time=snow_item["planned_start_date"], add_delta=False
                        ),
                        "QueueTimeExpiry": to_central_time(
                            time=snow_item["planned_start_date"], add_delta=True
                        ),
                    }

                    # if the release is successful it will return true and we post to webex
                    if schedule_release(deployment_resource=deployment_resource):
                        webex_message += "Status: **Successfully assigned ServiceNow item and scheduled deployment in Octopus Deploy.** \n"
                        webex_message += "_No further action needed._ \n"
                    else:
                        # if it fails post to webex about the failure
                        webex_message += (
                            "Status: **FAILED to schedule deployment in Octopus Deploy.** \n"
                            "_Possible Solutions:_ \n"
                            "   - Verify that at minimum five minutes have been alloted to schedule the deployment. \n"
                            "   - Verify that date and time in the ServiceNow item are correct. \n"
                            "   - Verify that the Octopus Deploy server is up and running.  \n"
                        )
                        assign_snow_item(snow_item=snow_item, assign_to_queue=True)
                    post_to_webex(message=webex_message)
                else:
                    webex_message += (
                        "Status: **Release has already been scheduled in Octopus Deploy!** \n"
                        "_Possible Solutions:_ \n"
                        "   - Deployment has previously been scheduled, but verify that the date and time match what is on Change Task.  \n"
                    )

                    post_to_webex(message=webex_message)
                    continue

def queued_deployments() -> list:
    """Retrieves queued deployments from Octopus Deploy"""

    # retrieve queued deployments
    results = requests.get(
        url=f"{scheduler_config['OctopusDeployBaseUrl']}{scheduler_config['TasksEndpoint']}?take=999",
        headers={"X-Octopus-ApiKey": f"{scheduler_config['OctopusDeployApiKey']}"},
        verify=False,
    )

    # we only want to results if code is 200, otherwise return empty list
    if results.status_code == 200:
        results = results.json()
        return results["Items"]
    else:
        log(results.text)
        return []
    
def filter_deployments(deployments: list) -> list:
    """
    Filters Octopus Deploy Deployments to specified critera
        Parameters:
            deployments: list of deployments from Octopus Deploy
    """
    return [
        deployment
        for deployment in deployments
        if deployment["State"] == "Queued"
        and deployment["State"] != "Canceled"
        and "Release Approval" not in deployment["Description"]
        and "Prod" in deployment["Description"]
    ]

def format_od_time(time_string) -> str:
    """Converts the Octopus Deploy timestamp to mach that of ServiceNOw

    Keyword arguments:
    time_string -- datetime string
    Return: str
    """

    time_string = time_string.replace(".000", "")
    return (
        datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S%z")
        .astimezone(pytz.timezone("US/Central"))
        .isoformat()
    )
    
def authorize_deployments(snow_items: list, deployments: list) -> None:
    """
    Verifies that each queued deployment in OD has a SNOW item that corresponds with the version number
        Parameters:
            snow_items: List of items from SNOW
            deployments: Dict of OD queued deployments
    """

    # list comprehension to filter out nonessential task items that do not relate to deployments
    # we need this to be as specific as possible so that we do not cancel any queued tasks that are
    # not production deployments with no change tickets
    deployments = filter_deployments(deployments)

    # we only want to loop through if we have deployments
    if deployments:
        # placeholder for the webex message
        webex_message = ""

        for deployment in deployments:
            # no deployment has yet been found so set initially to false
            found = False

            release_number = extract_release(deployment["Description"]).upper()
            project_name = find_project_name(deployment["Description"]).upper()

            # now that we have the release we need to check for a change task
            if snow_items:
                for snow_item in snow_items:
                    # we need to convert the date and time of OD and SNOW to match either other
                    deployment_time = format_od_time(
                        time_string=deployment["QueueTime"]
                    )
                    snow_time = to_central_time(
                        snow_item["planned_start_date"], add_delta=False
                    )
                    snow_release_number = extract_release(
                        snow_item["short_description"]
                    )
                    snow_project_name = find_project_name(
                        snow_item["short_description"]
                    )

                    # if a release number and project is found set it to true
                    if project_name == snow_project_name.upper():
                        if release_number == snow_release_number.upper():
                            if deployment_time == snow_time:
                                found = True
                                break

            # if we go through the entire collection of service now items and do not find a release then it is
            # unauthorized deployment and needs to be canceled
            if not found:
                if cancel_deployment(id=deployment["Id"]):
                    webex_message = (
                        f"Deployment **{deployment['Description']}** was cancelled because there was no Change Task matching the deployment info in Octopus Deploy. \n"
                        "   - If a Change or Task has been pulled and then added back into the ServiceNow queue it will automatically be rescheduled within 2 run cycles. \n"
                        "   - If the deployment time or release number on the Change Task has changed it will automatically be rescheduled. \n"
                        "_No further action needed._ \n"
                    )
                else:
                    webex_message = (
                        f"**{deployment['Description']}** does not have an associated Change Task. Attemped to cancel but encountered an error. \n"
                        "_Possible solutions:_ \n"
                        "   - Associate a Change Task with this release. \n"
                        "   - Cancel deployment manually. \n"
                    )

                post_to_webex(message=webex_message)

                # assign ticket back to queue if there is one because there is no valid change task when release numbers change
                for snow_item in snow_items:
                    if project_name in str(snow_item["short_description"]).upper():
                        assign_snow_item(snow_item=snow_item, assign_to_queue=True)

def cancel_deployment(id: str) -> bool:
    """
    Cancels deployment if there is no SNOW ticket
        Parameters:
            id: id of OD deployment
    """
    if id:
        try:
            results = requests.post(
                url=f"{scheduler_config['OctopusDeployBaseUrl']}{scheduler_config['TasksEndpoint']}/{id}/cancel",
                headers={
                    "X-Octopus-ApiKey": f"{scheduler_config['OctopusDeployApiKey']}"
                },
                verify=False,
            )
        except Exception as e:
            error_string = str(e)
            log(error_string)
            return False

        if results.status_code == 200:
            return True
        else:
            log(results.text)
            return False
    else:
        return False

def export_to_file(data, filename):
    """
    Exports the given data to a human-readable text file.
    """
    with open(filename, 'w') as file:
        for section, items in data.items():
            file.write(f"{section}:\n")
            if "error" in items:
                file.write(f"Error: {items['error']}\n")
            else:
                for item in items.get('result', []):
                    file.write(f"Task Number: {item.get('number', 'N/A')}\n")
                    file.write(f"Short Description: {item.get('short_description', 'N/A')}\n")
                    file.write("\n")
            file.write("\n")
    print(f"[SUCCESS] Data exported to {filename}")


# ---- Run Method (From main.py) ----
def run():
    print("\n--------------------")
    print(f"PROCESS STARTED {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}")
    print(f"ENVIRONMENT: {os.getenv('ASPNETCORE_ENVIRONMENT', 'Development').upper()}")

    change_task_data = get_change_tasks()
    unassign_tasks = [
        task for task in change_task_data.get("result", [])
        if task.get("assigned_to", {}).get("display_value", "").lower() == "autooctopus"
        and "PROCESSED" not in task.get("short_description", "").upper()
    ]
    print(f"UNASSIGN TASK COUNT: {len(unassign_tasks)}")
    print("--------------------")

    unassigned_tasks = [
        task for task in change_task_data.get("result", [])
        if task.get("assigned_to", {}).get("display_value", "").lower() != "autooctopus"
    ]
    print(f"UNASSIGNED TASK COUNT: {len(unassigned_tasks)}")
    print("--------------------")

    if unassigned_tasks:
        print("[INFO] Scheduling change tasks...")
        schedule(unassigned_tasks)
    print("--------------------")

    deployments = queued_deployments()
    print(f"QUEUED DEPLOYMENTS COUNT: {len(deployments)}")
    print("--------------------")

    assigned_tasks = [
        task for task in change_task_data.get("result", [])
        if task.get("assigned_to", {}).get("display_value", "").lower() == "autooctopus"
    ]
    print(f"ASSIGNED TASK COUNT: {len(assigned_tasks)}")
    print("--------------------")

    authorize_deployments(snow_items=assigned_tasks, deployments=deployments)
    print("--------------------")

    print(f"PROCESS FINISHED {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}")
    print("--------------------")

# ---- Main Method ----
def main():
    run()

if __name__ == "__main__":
    main()

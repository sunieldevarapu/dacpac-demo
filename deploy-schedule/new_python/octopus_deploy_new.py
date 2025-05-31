import pytz
import requests
from datetime import datetime, timedelta
from pytz import utc, timezone
import re
import os
import logging
from service_now_new import assign_snow_item
from webex import post_to_webex
from logwrite import log

# Setup logging for GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def log(message):
    """Log messages to stdout for GitHub Actions logs"""
    logger.info(message)

# Import after defining the log function to avoid circular import issues
#from sched.service_now import assign_snow_item
from service_now_new import assign_snow_item

# Initialize scheduler_config from environment variables and secrets
scheduler_config = {
    'OctopusDeployBaseUrl': os.environ.get('OCTOPUS_DEPLOY_BASE_URL'),
    'TasksEndpoint': os.environ.get('OCTOPUS_TASKS_ENDPOINT', '/api/tasks'),
    'ReleaseEndpoint': os.environ.get('OCTOPUS_RELEASE_ENDPOINT', '/api/releases'),
    'DeploymentEndpoint': os.environ.get('OCTOPUS_DEPLOYMENT_ENDPOINT', '/api/deployments'),
    'ProjectsEndpoint': os.environ.get('OCTOPUS_PROJECTS_ENDPOINT', '/api/projects/all'),
    'OctopusDeployApiKey': os.environ.get('OCTOPUS_DEPLOY_API_KEY'),
    'Environment': os.environ.get('ASPNETCORE_ENVIRONMENT', 'Development')
}


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

# TODO Seems inefficient to query all projects in OD just to remove the project name
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

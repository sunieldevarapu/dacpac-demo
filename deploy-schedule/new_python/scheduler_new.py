from octopus_deploy_new import *
from service_now_new import *
from webex import *
#from cmadevops_deployment_scheduler.config.config import scheduler_config
from datetime import datetime
import os

# Initialize scheduler_config from environment variables and secrets
scheduler_config = {
    'BaseUrl': os.environ.get('SNOW_BASE_URL'),
    'QueryChangeTaskEndpoint': os.environ.get('SNOW_QUERY_CHANGE_TASK_ENDPOINT', '/api/now/table/change_task'),
    'UpdateChangeTaskEndpoint': os.environ.get('SNOW_UPDATE_CHANGE_TASK_ENDPOINT', '/api/now/table/change_task'),
    'ApiAuthentication': {
        'Username': os.environ.get('SNOW_USERNAME'),
        'Password': os.environ.get('SNOW_PASSWORD')
    },
    'AutomationUserId': os.environ.get('SNOW_AUTOMATION_USER_ID'),
    'ChsDevOpsSoftwareSolutionsId': os.environ.get('SNOW_DEV_OPS_SOFTWARE_SOLUTIONS_ID'),
    
    'OctopusDeployBaseUrl': os.environ.get('OCTOPUS_DEPLOY_BASE_URL'),
    'TasksEndpoint': os.environ.get('OCTOPUS_TASKS_ENDPOINT', '/api/tasks'),
    'ReleaseEndpoint': os.environ.get('OCTOPUS_RELEASE_ENDPOINT', '/api/releases'),
    'DeploymentEndpoint': os.environ.get('OCTOPUS_DEPLOYMENT_ENDPOINT', '/api/deployments'),
    'ProjectsEndpoint': os.environ.get('OCTOPUS_PROJECTS_ENDPOINT', '/api/projects/all'),
    'OctopusDeployApiKey': os.environ.get('OCTOPUS_DEPLOY_API_KEY'),
    'Environment': os.environ.get('ASPNETCORE_ENVIRONMENT', 'Production')
}

def convert_utc_offset(date_string: str):
    """
    Converts UTC offset to Central Time
        Parameters:
            date_string: datetime string to be converted to central time
    """
    return (datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")).strftime(
        "%Y-%m-%d %H:%M"
    )


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

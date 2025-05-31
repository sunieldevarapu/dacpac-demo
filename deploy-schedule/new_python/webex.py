import requests
#from cmadevops_deployment_scheduler.config.config import scheduler_config
from urllib3.exceptions import InsecureRequestWarning
from logwrite import log
import os

# disables console logging of insecure  https
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
    
scheduler_config = {
    'BaseUrl': os.environ.get('SNOW_BASE_URL'),
    'QueryChangeTaskEndpoint': os.environ.get('SNOW_QUERY_CHANGE_TASK_ENDPOINT', '/api/now/table/change_task'),
    'UpdateChangeTaskEndpoint': os.environ.get('SNOW_UPDATE_CHANGE_TASK_ENDPOINT', '/api/now/table/change_task'),
    'ApiAuthentication': {
        'Username': os.environ.get('SNOW_USERNAME'),
        'Password': os.environ.get('SNOW_PASSWORD')
    },
    'AutomationUserId': os.environ.get('SNOW_AUTOMATION_USER_ID'),
    'ChsDevOpsSoftwareSolutionsId': os.environ.get('SNOW_DEV_OPS_SOFTWARE_SOLUTIONS_ID')
}

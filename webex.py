import requests
from cmadevops_deployment_scheduler.config.config import scheduler_config
from urllib3.exceptions import InsecureRequestWarning
from cmadevops_deployment_scheduler.modules.logwrite import log

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

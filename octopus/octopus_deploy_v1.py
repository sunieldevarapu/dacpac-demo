# from octopus_deploy_new import *
# from scheduler_new import *
# import json
import requests

# with open('./cmadevops_deployment_scheduler/modules/output1.json', 'r') as file:
#     snow_items = json.loads(file.read())
#     file.close()

deployment_resource = {
    "ReleaseId": "Release-1",
    "ProjectId": "Project-1",
    "ChannelId": "Channel-1",
    "EnvironmentId":"Environment-123",
    "QueueTime": "2025-05-08T06:30:00",
    "QueueTimeExpiry":"2025-05-08T09:30:00"
}

# Call schedule method
# schedule(snow_items)

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
        try:
            print("**********Inside try block before requests call**********")
            results = requests.post(
                url="https://octopusdeploydev.silver.com/api/deployments",
                headers={"X-Octopus-ApiKey": "API-TF21J6OCQK1HONXEQ95BYJWZJLTMETKB"},
                json=deployment_resource,
                verify=False,
            )
            print("**********Inside try block after requests call**********")
    
            # if the result status code is not 201 then something failed
            if results.status_code == 201:
                print("**********Inside if statement**********")
                return True
            else:
                print("**********Inside else statement**********")
                log(results.status_code)
                results = results.json()
                # log(results["Errors"].text)
                return False
        except requests.exceptions.ConnectionError as e:
            print("**********Inside exception block**********")
            r = "No response"
    else:
        return False

# Call Octopus method
schedule_release(deployment_resource)

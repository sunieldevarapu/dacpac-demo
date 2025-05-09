import requests

deployment_resource = {
    "ReleaseId": "Release-1",
    "ProjectId": "Project-1",
    "ChannelId": "Channel-1",
    "EnvironmentId": "Environment-123",
    "QueueTime": "2025-05-08T06:30:00",
    "QueueTimeExpiry": "2025-05-08T09:30:00"
}

def schedule_release(deployment_resource: dict) -> bool:
    """
    Schedules release in Octopus Deploy
    """
    if deployment_resource:
        try:
            print("**********Inside try block before requests call**********")
            results = requests.post(
                url="https://deploydev.blue.com/api/deployments",
                headers={"X-Octopus-ApiKey": "API-xxxxxxxxxxxx"},
                json=deployment_resource,
                verify=False,
            )
            print("**********Inside try block after requests call**********")
            print("Status Code:", results.status_code)
            print("Response Body:", results.text)

            if results.status_code == 201:
                print("**********Inside if statement**********")
                return True
            else:
                print("**********Inside else statement**********")
                return False

        except requests.exceptions.RequestException as e:
            print("**********Inside exception block**********")
            print("Request failed:", str(e))
            return False
    else:
        print("Deployment resource is empty.")
        return False

# Call Octopus method
schedule_release(deployment_resource)

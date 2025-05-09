import requests

deployment_resource = {
    "ReleaseId": "Release-1",
    "ProjectId": "Project-1",
    "ChannelId": "Channel-1",
    "EnvironmentId": "Environment-123",
    "QueueTime": "2025-05-08T06:30:00",
    "QueueTimeExpiry": "2025-05-08T09:30:00"
}

response = requests.post(
    url="https://your-octopus-server/api/deployments",
    headers={"X-Octopus-ApiKey": "API-YourActualKey"},
    json=deployment_resource,
    verify=False  # Set to True in production
)

print("Status Code:", response.status_code)
print("Response Body:", response.text)

import requests
import os
from datetime import datetime, timedelta

def to_central_time(deployment_time, is_dst):
    # Convert UTC time to Central Time (CT)
    central_time = deployment_time - timedelta(hours=5 if is_dst else 6)
    return central_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# Environment variables (replace with your actual values or set them in your environment)
octopus_server = os.getenv('OCTOPUS_SERVER', 'https://your-octopus-server')
api_key = os.getenv('OCTOPUS_API_KEY', 'your-api-key')
release_id = os.getenv('RELEASE_ID', 'your-release-id')
project_id = os.getenv('PROJECT_ID', 'your-project-id')
channel_id = os.getenv('CHANNEL_ID', 'your-channel-id')
environment_id = os.getenv('ENVIRONMENT_ID', 'Environment-123')
deployment_time_str = os.getenv('DEPLOYMENT_TIME', '2025-05-08T02:00:00Z')

# Parse the deployment time
deployment_time = datetime.strptime(deployment_time_str, '%Y-%m-%dT%H:%M:%SZ')

# Convert to Central Time
queue_time = to_central_time(deployment_time, False)

# API endpoint and headers
url = f"{octopus_server}/api/deployments"
headers = {
    'X-Octopus-ApiKey': api_key,
    'Content-Type': 'application/json'
}

# Payload for the deployment request
payload = {
    'ReleaseId': release_id,
    'ProjectId': project_id,
    'ChannelId': channel_id,
    'EnvironmentId': environment_id,
    'QueueTime': queue_time,
    'QueueTimeExpiry': queue_time
}

# Make the API request to schedule the deployment
response = requests.post(url, json=payload, headers=headers)

# Print the response (deployment details)
print(response.json())

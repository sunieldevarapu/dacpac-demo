import os
import requests
from requests.auth import HTTPBasicAuth

def get_servicenow_data(endpoint, params=None):
    """
    Makes a GET request to the ServiceNow API using basic authentication.

    Args:
        instance_url (str): The base URL of the ServiceNow instance (e.g., 'https://your_instance.service-now.com').
        endpoint (str): The API endpoint to call (e.g., '/api/now/table/incident').
        username (str): Your ServiceNow username.
        password (str): Your ServiceNow password.
        params (dict, optional): Dictionary of query parameters to include in the request.

    Returns:
        dict: JSON responce from the API if successful, or error details.
    """
    
    instance_url = "https://.service-now.com"
    username = ""
    password = ""

    url = f"{instance_url}{endpoint}"
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
   
query_ctask_endpoint = "/api/now/table/change_task?sysparm_query="
update_ctask_endpoint = "/api/now/table/change_task"

data = get_servicenow_data(query_ctask_endpoint)
print(data)

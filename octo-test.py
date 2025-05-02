import requests

# Define the URL, username, and password
url = "https://your-instance.service-now.com/api/now/table/your_table"
username = "your-username"
password = "your-password"

def log_in(url, username, password):
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        print("Success")
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print("Invalid credentials")
        else:
            print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

# Call the login function
log_in(url, username, password)

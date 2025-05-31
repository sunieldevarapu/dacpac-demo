def log(message: str) -> str:
    """Writes to log file"""
    with open("log.txt", "a") as line:
        line.write(message)

=====================================================================================

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
    'ChsDevOpsSoftwareSolutionsId': os.environ.get('SNOW_DEV_OPS_SOFTWARE_SOLUTIONS_ID')
}

# Check for missing environment variables
required_env_vars = ['SNOW_BASE_URL', 'SNOW_USERNAME', 'SNOW_PASSWORD']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Debug print (remove in production)
print("SNOW_USERNAME:", scheduler_config["ApiAuthentication"]["Username"])
print("SNOW_PASSWORD:", scheduler_config["ApiAuthentication"]["Password"])

# Log authentication attempt
log(f"Attempting ServiceNow API connection to {scheduler_config['BaseUrl']} as user {scheduler_config['ApiAuthentication']['Username']}")


=============================================================================================

# Set your ServiceNow instance URL and credentials
$baseUrl = "https://<your-instance>.service-now.com"
$username = "your_username"
$password = "your_password"

# Create a credential object
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ($username, $securePassword)

# Make a test API call to the change_task table
$response = Invoke-RestMethod -Uri "$baseUrl/api/now/table/change_task?sysparm_limit=1" `
                              -Method Get `
                              -Credential $credential `
                              -Headers @{ "Accept" = "application/json" }

# Display the response
$response


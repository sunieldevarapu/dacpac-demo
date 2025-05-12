name: Deployment Scheduler and Octopus Deploy

on:
  schedule:
    # Run every hour
    - cron: '0 * * * *'
  workflow_dispatch:
    inputs:
      action:
        description: 'Action to perform'
        required: true
        default: 'schedule'
        type: choice
        options:
          - schedule
          - deploy
      releaseNumber:
        description: 'Release number to deploy (only for deploy action)'
        required: false
      projectName:
        description: 'Project name in Octopus Deploy (only for deploy action)'
        required: false
      deploymentTime:
        description: 'Deployment time (YYYY-MM-DD HH:MM:SS) (only for deploy action)'
        required: false

env:
  # General environment settings
  ASPNETCORE_ENVIRONMENT: ${{ vars.ASPNETCORE_ENVIRONMENT || 'development' }}
  
  # ServiceNow configuration
  SNOW_BASE_URL: 'https://servicenowinstance.service-now.com'
  SNOW_QUERY_CHANGE_TASK_ENDPOINT: '/api/now/table/change_task'
  SNOW_UPDATE_CHANGE_TASK_ENDPOINT: '/api/now/table/change_task'
  SNOW_USERNAME: ${{ secrets.SNOW_USERNAME }}
  SNOW_PASSWORD: ${{ secrets.SNOW_PASSWORD }}
  SNOW_AUTOMATION_USER_ID: ${{ secrets.SNOW_AUTOMATION_USER_ID }}
  SNOW_DEV_OPS_SOFTWARE_SOLUTIONS_ID: ${{ secrets.SNOW_DEV_OPS_SOFTWARE_SOLUTIONS_ID }}
  
  # Octopus Deploy configuration
  OCTOPUS_DEPLOY_BASE_URL: 'https://octopus.company.com'
  OCTOPUS_TASKS_ENDPOINT: '/api/tasks'
  OCTOPUS_RELEASE_ENDPOINT: '/api/releases'
  OCTOPUS_DEPLOYMENT_ENDPOINT: '/api/deployments'
  OCTOPUS_PROJECTS_ENDPOINT: '/api/projects/all'
  OCTOPUS_DEPLOY_API_KEY: ${{ secrets.OCTOPUS_DEPLOY_API_KEY }}
  OCTOPUS_ENVIRONMENT_ID: ${{ secrets.OCTOPUS_ENVIRONMENT_ID }}

jobs:
octopus-deploy:
    runs-on: ubuntu-latest
    if: github.event.inputs.action == 'deploy'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Find Project ID
        id: find_project
        run: |
          # Query Octopus Deploy for all projects
          PROJECTS_RESPONSE=$(curl -s -H "X-Octopus-ApiKey: ${{ env.OCTOPUS_DEPLOY_API_KEY }}" \
            "${{ env.OCTOPUS_DEPLOY_BASE_URL }}${{ env.OCTOPUS_PROJECTS_ENDPOINT }}?take=999")
          
          # Extract project ID by filtering for the project name
          PROJECT_ID=$(echo $PROJECTS_RESPONSE | jq -r --arg name "${{ github.event.inputs.projectName }}" \
            '.Items[] | select(.Name == $name) | .Id')
          
          if [ -z "$PROJECT_ID" ]; then
            echo "::error::Project ${{ github.event.inputs.projectName }} not found"
            exit 1
          fi
          
          echo "project_id=$PROJECT_ID" >> $GITHUB_OUTPUT
          echo "Found project ID: $PROJECT_ID"

      - name: Find Release
        id: find_release
        run: |
          # Query Octopus Deploy for releases for the project
          RELEASES_RESPONSE=$(curl -s -H "X-Octopus-ApiKey: ${{ env.OCTOPUS_DEPLOY_API_KEY }}" \
            "${{ env.OCTOPUS_DEPLOY_BASE_URL }}${{ env.OCTOPUS_PROJECTS_ENDPOINT }}/${{ steps.find_project.outputs.project_id }}/releases?take=999")
          
          # Extract the release information based on version number
          RELEASE_JSON=$(echo $RELEASES_RESPONSE | jq -r --arg version "${{ github.event.inputs.releaseNumber }}" \
            '.Items[] | select(.Version == $version)')
          
          if [ -z "$RELEASE_JSON" ]; then
            echo "::error::Release ${{ github.event.inputs.releaseNumber }} not found for project ${{ github.event.inputs.projectName }}"
            exit 1
          fi
          
          RELEASE_ID=$(echo $RELEASE_JSON | jq -r '.Id')
          CHANNEL_ID=$(echo $RELEASE_JSON | jq -r '.ChannelId')
          
          echo "release_id=$RELEASE_ID" >> $GITHUB_OUTPUT
          echo "channel_id=$CHANNEL_ID" >> $GITHUB_OUTPUT
          echo "Found release ID: $RELEASE_ID"

      - name: Prepare Deployment Times
        id: prepare_times
        run: |
          # Convert deployment time to UTC and format for Octopus Deploy
          # Add the deployment time as is (assuming it's in the format YYYY-MM-DD HH:MM:SS)
          DEPLOY_TIME="${{ github.event.inputs.deploymentTime }}"
          
          # Convert to ISO 8601 format with timezone for Octopus Deploy
          # We'll use date command to handle the conversion
          QUEUE_TIME=$(date -d "$DEPLOY_TIME" -u +"%Y-%m-%dT%H:%M:%S%:z")
          
          # Calculate expiry time (deployment time + 30 minutes)
          QUEUE_TIME_EXPIRY=$(date -d "$DEPLOY_TIME 30 minutes" -u +"%Y-%m-%dT%H:%M:%S%:z")
          
          echo "queue_time=$QUEUE_TIME" >> $GITHUB_OUTPUT
          echo "queue_time_expiry=$QUEUE_TIME_EXPIRY" >> $GITHUB_OUTPUT

      - name: Schedule Deployment
        id: schedule_deployment
        run: |
          # Create deployment resource JSON
          DEPLOYMENT_RESOURCE=$(cat <<EOF
          {
            "ReleaseId": "${{ steps.find_release.outputs.release_id }}",
            "ProjectId": "${{ steps.find_project.outputs.project_id }}",
            "ChannelId": "${{ steps.find_release.outputs.channel_id }}",
            "EnvironmentId": "${{ env.OCTOPUS_ENVIRONMENT_ID }}",
            "QueueTime": "${{ steps.prepare_times.outputs.queue_time }}",
            "QueueTimeExpiry": "${{ steps.prepare_times.outputs.queue_time_expiry }}"
          }
          EOF
          )
          
          # Schedule the deployment in Octopus Deploy
          DEPLOYMENT_RESULT=$(curl -s -X POST -H "Content-Type: application/json" \
            -H "X-Octopus-ApiKey: ${{ env.OCTOPUS_DEPLOY_API_KEY }}" \
            -d "$DEPLOYMENT_RESOURCE" \
            "${{ env.OCTOPUS_DEPLOY_BASE_URL }}${{ env.OCTOPUS_DEPLOYMENT_ENDPOINT }}")
          
          # Check if deployment was successful (HTTP 201 Created)
          DEPLOYMENT_ID=$(echo $DEPLOYMENT_RESULT | jq -r '.Id // empty')
          
          if [ -z "$DEPLOYMENT_ID" ]; then
            ERROR_MESSAGE=$(echo $DEPLOYMENT_RESULT | jq -r '.ErrorMessage // "Failed to schedule deployment"')
            echo "::error::$ERROR_MESSAGE"
            exit 1
          fi
          
          echo "deployment_id=$DEPLOYMENT_ID" >> $GITHUB_OUTPUT
          echo "Successfully scheduled deployment for ${{ github.event.inputs.releaseNumber }} of ${{ github.event.inputs.projectName }} (ID: $DEPLOYMENT_ID)"

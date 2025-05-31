import sys
import os
from pathlib import Path
from datetime import datetime
import pytz

# Add the parent directory to Python path so cmadevops_deployment_scheduler can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from octopus_deploy_new import *
from service_now_new import *
from scheduler_new import *
from logwrite import log


def test_servicenow_connection():
    """Test ServiceNow API connection using a basic call"""
    log("----- ServiceNow API Connection Test -----")
    try:
        tasks = change_tasks(assigned_to=False)
        if tasks:
            log(f"[SUCCESS] Connected to ServiceNow. Retrieved {len(tasks)} unassigned change task(s).")
        else:
            log("[WARNING] Connected to ServiceNow, but no unassigned change tasks were found.")
    except Exception as e:
        log(f"[ERROR] Failed to connect to ServiceNow API: {str(e)}")
    log("----- End ServiceNow API Connection Test -----\n")


def run():
    """Entry point for Deployment Scheduler"""
    log("--------------------\n")
    log(f"PROCESS STARTED {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n")
    log(f"ENVIRONMENT: {os.getenv('ASPNETCORE_ENVIRONMENT', 'development').upper()}\n")

    # Test the ServiceNow API connection first
    test_servicenow_connection()

    # Step 1: Unassign already-assigned tasks if needed
    unassign(snow_items=change_tasks(assigned_to=True))
    log(f"UNASSIGN complete: {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n")
    log("-------------------- \n")

    # Step 2: Get unassigned tasks
    unassigned_tasks = change_tasks(assigned_to=False)
    log(f"Retrieved {len(unassigned_tasks)} unassigned task(s).\n")
    log(f"GET TASKS: {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n")
    log("-------------------- \n")

    # Step 3: Schedule change tasks
    if unassigned_tasks:
        log("Scheduling unassigned tasks...\n")
        schedule(snow_items=unassigned_tasks)
    else:
        log("No unassigned tasks found to schedule.\n")
    log(f"SCHEDULE complete: {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n")
    log("-------------------- \n")

    # Step 4: Get tasks already assigned to AUTOOCTOPUS
    assigned_tasks = change_tasks(assigned_to=True)
    log(f"Retrieved {len(assigned_tasks)} assigned task(s).\n")
    log(f"GET ASSIGNED TASKS: {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n")
    log("-------------------- \n")

    # Optional: Deployment authorization logic (currently commented out)
    # deployments = queued_deployments()
    # authorize_deployments(snow_items=assigned_tasks, deployments=deployments)

    log(f"PROCESS FINISHED {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n")
    log("-------------------- \n")


def main():
    run()


if __name__ == "__main__":
    main()

import argparse
from datetime import datetime
import pytz

def print_timestamped(message):
    now = datetime.now().astimezone(pytz.timezone('US/Central'))
    print(f"{message} {now.strftime('%Y-%m-%d %H:%M CST')}")
    print('--------------------')

def unassign_tasks(assigned_tasks):
    print_timestamped("PROCESS STARTED")
    print("ENVIRONMENT: development")
    print("Unassigning tasks assigned to AUTOOCTOPUS...")
    for task in assigned_tasks:
        print(f"Unassigned task: {task['id']} - {task['description']}")
    print_timestamped("UNASSIGN")

def schedule_tasks(unassigned_tasks):
    print("Getting unassigned tasks...")
    for task in unassigned_tasks:
        print(f"Unassigned task: {task['id']} - {task['description']}")
    print_timestamped("GET TASKS")

    if unassigned_tasks:
        print("Scheduling tasks...")
        for task in unassigned_tasks:
            print(f"Scheduled task: {task['id']} - {task['description']}")
        print_timestamped("SCHEDULE")

def authorize_deployments(assigned_tasks, queued_deployments):
    print("Getting queued deployments...")
    for deploy in queued_deployments:
        print(f"Queued deployment: {deploy['id']} - {deploy['project']}")
    print_timestamped("GET QUEUED DEPLOYMENTS")

    print("Getting assigned tasks...")
    for task in assigned_tasks:
        print(f"Assigned task: {task['id']} - {task['description']}")
    print_timestamped("GET ASSIGNED TASKS")

    print("Authorizing deployments...")
    for deploy in queued_deployments:
        print(f"Authorized deployment: {deploy['id']} for project {deploy['project']}")
    print_timestamped("AUTHORIZE DEPLOYMENTS")
    print_timestamped("PROCESS FINISHED")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deployment Scheduler Test Cases")
    parser.add_argument(
        "--test-case",
        choices=["default", "no-unassigned", "no-assigned", "custom"],
        default="default",
        help="Choose which test case to run"
    )
    args = parser.parse_args()

    # Default test data
    unassigned_tasks = [
        {"id": "CTASK001", "description": "Update deployment pipeline"},
        {"id": "CTASK002", "description": "Review change request"}
    ]
    assigned_tasks = [
        {"id": "CTASK003", "description": "Deploy to staging"},
        {"id": "CTASK004", "description": "Deploy to production"}
    ]
    queued_deployments = [
        {"id": "DEPLOY001", "project": "Project A"},
        {"id": "DEPLOY002", "project": "Project B"}
    ]

    # Modify based on test case
    if args.test_case == "no-unassigned":
        unassigned_tasks = []
    elif args.test_case == "no-assigned":
        assigned_tasks = []
    elif args.test_case == "custom":
        unassigned_tasks = [{"id": "CTASK999", "description": "Custom unassigned task"}]
        assigned_tasks = [{"id": "CTASK888", "description": "Custom assigned task"}]
        queued_deployments = [{"id": "DEPLOY999", "project": "Custom Project"}]

    # Run the workflow
    unassign_tasks(assigned_tasks)
    schedule_tasks(unassigned_tasks)
    authorize_deployments(assigned_tasks, queued_deployments)

'''
1. Default Case (both assigned and unassigned tasks)
python deployment_scheduler.py --test-case default

2. No Unassigned Tasks
python deployment_scheduler.py --test-case no-unassigned

3. No Assigned Tasks
python deployment_scheduler.py --test-case no-assigned

4. Custom Test Case
python deployment_scheduler.py --test-case custom

'''

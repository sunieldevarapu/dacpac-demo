from datetime import datetime
import pytz

# Simulated hardcoded unassigned tasks (requirement #3)
unassigned_tasks = [
    {"id": "CTASK001", "description": "Update deployment pipeline"},
    {"id": "CTASK002", "description": "Review change request"}
]

# Simulated assigned tasks
assigned_tasks = [
    {"id": "CTASK003", "description": "Deploy to staging"},
    {"id": "CTASK004", "description": "Deploy to production"}
]

# Simulated queued deployments
queued_deployments = [
    {"id": "DEPLOY001", "project": "Project A"},
    {"id": "DEPLOY002", "project": "Project B"}
]

def print_timestamped(message):
    now = datetime.now().astimezone(pytz.timezone('US/Central'))
    print(f"{message} {now.strftime('%Y-%m-%d %H:%M CST')}")
    print('--------------------')

def unassign_tasks():
    print_timestamped("PROCESS STARTED")
    print("ENVIRONMENT: development")
    print("Unassigning tasks assigned to AUTOOCTOPUS...")
    # Simulated unassignment logic
    for task in assigned_tasks:
        print(f"Unassigned task: {task['id']} - {task['description']}")
    print_timestamped("UNASSIGN")

def schedule_tasks():
    print("Getting unassigned tasks...")
    for task in unassigned_tasks:
        print(f"Unassigned task: {task['id']} - {task['description']}")
    print_timestamped("GET TASKS")

    if unassigned_tasks:
        print("Scheduling tasks...")
        for task in unassigned_tasks:
            print(f"Scheduled task: {task['id']} - {task['description']}")
        print_timestamped("SCHEDULE")

def authorize_deployments():
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
    unassign_tasks()
    schedule_tasks()
    authorize_deployments()

'''
Run the Script Normally
This will test the default hardcoded values for both assigned and unassigned tasks.

python deployment_scheduler.py


You should see output like:

PROCESS STARTED 2025-05-16 04:00 CST
ENVIRONMENT: development
Unassigning tasks assigned to AUTOOCTOPUS...
Unassigned task: CTASK003 - Deploy to staging
Unassigned task: CTASK004 - Deploy to production
UNASSIGN 2025-05-16 04:00 CST
--------------------
...
🧪 3. Test with No Unassigned Tasks
To simulate a scenario where there are no unassigned tasks, modify the unassigned_tasks list in the script:
unassigned_tasks = []

Then rerun:
python deployment_scheduler.py

You should see that the scheduling step is skipped:

Getting unassigned tasks...
GET TASKS 2025-05-16 04:05 CST
--------------------
(no scheduling output)
🧪 4. Test with No Assigned Tasks
To simulate a scenario where there are no assigned tasks, modify the assigned_tasks list:
assigned_tasks = []


Then rerun:

python deployment_scheduler.py


You’ll see that the unassign and authorize steps don’t process any tasks:

Unassigning tasks assigned to AUTOOCTOPUS...
UNASSIGN 2025-05-16 04:10 CST
--------------------
...
Getting assigned tasks...
GET ASSIGNED TASKS 2025-05-16 04:10 CST
--------------------
Authorizing deployments...
(no deployments authorized)
'''

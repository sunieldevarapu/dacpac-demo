from cmadevops_deployment_scheduler.modules.octopus_deploy import *
from cmadevops_deployment_scheduler.modules.service_now import *
from cmadevops_deployment_scheduler.modules.scheduler import *
from cmadevops_deployment_scheduler.modules.logwrite import log


import os

# TODO: Add more detailed logging to scheduler for debugging. We need to be able to see what it is doing as it goes through the process. 
# TODO: Tag user in channel when there is something wrong with a change
# TODO: This falls under NICE TO HAVE, but fix unit tests. 

def run():
    """Entry point for Deployment Scheduler"""
    log("--------------------\n")
    log(
        f"PROCESS STARTED {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log(f"ENVIRONMENT: {os.getenv('ASPNETCORE_ENVIRONMENT').upper()}\n")
    # sometimes change tasks get put in our queue already assigned to the AUTOOCTOPUS account
    # this will unassign it for automation to pick it up if the title does not contain PROCESSED
    # UNASSIGN is an experimental feature, while it works we were having some issues with it. More testing is needed before it can be put into production.
    unassign(snow_items=change_tasks(assigned_to=True))
    log(
        f"UNASSIGN {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log("-------------------- \n")

    # get tasks that are NOT ASSIGNED to AUTOOCTOPUS from SNOW
    unassigned_tasks = change_tasks(assigned_to=False)
    log(
        f"GET TASKS {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log("-------------------- \n")

    # schedule change tasks
    if len(unassigned_tasks) > 0:
        schedule(snow_items=unassigned_tasks)
    log(
        f"SCHEDULE {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log("-------------------- \n")

    # get queued deployments from OD
    deployments = queued_deployments()
    log(
        f"GET QUEUED DEPLOYMENTS {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log("-------------------- \n")

    # get tasks that ARE ASSIGNED to AUTOOCTOPUS from SNOW
    # the purpose of this is we only want to authorize deployments with tasks that are already assigned
    # the deployment will get cancelled on the next run due it not finding a task since it has been assigned to AUTOOCTOPUS
    assigned_tasks = change_tasks(assigned_to=True)
    log(
        f"GET ASSIGNED TASKS {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log("-------------------- \n")

    # authorize current queued deployments  10/28/23 commented out due to errors on go-live of OD migration
    authorize_deployments(snow_items=assigned_tasks, deployments=deployments)
    log(
        f"AUTHORIZE DEPLOYMENTS {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log("-------------------- \n")

    log(
        f"PROCESS FINISHED {datetime.now().astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST')}\n"
    )
    log("-------------------- \n")


def main():
    run()


if __name__ == "__main__":
    main()

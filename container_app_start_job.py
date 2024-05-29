from enum import Enum

import typer
from azure.identity import DefaultAzureCredential
from azure.mgmt.appcontainers import ContainerAppsAPIClient

subscription_id: str = "a6feefeb-7f6b-425b-8311-b42ebeaee0d1"
resource_group_name: str = "johannes-sandbox"


class JobNames(str, Enum):
    STORAGE_QUEUE = "storage-queue"
    SERVICE_BUS_QUEUE = "service-bus-queue"


def execute_job(job_name: JobNames):
    credential = DefaultAzureCredential()

    client = ContainerAppsAPIClient(
        credential=credential,
        subscription_id=subscription_id,
    )

    job_definition = client.jobs.get(
        resource_group_name=resource_group_name, job_name=job_name
    )

    print(job_definition)

    job_start = client.jobs.begin_start(
        resource_group_name=resource_group_name,
        job_name=job_name,
    ).result()
    print(job_start.name, job_start.id)

    job_execution = client.job_execution(
        resource_group_name=resource_group_name,
        job_name=job_name,
        job_execution_name=job_start.name,
    )

    print(job_execution)


if __name__ == "__main__":
    typer.run(execute_job)

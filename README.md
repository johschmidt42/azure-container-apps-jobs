# Azure Container Apps Jobs

This repository explores the **Azure Container Apps Jobs**
for [Queue based point-to-point communication](https://learn.microsoft.com/en-us/azure/container-apps/tutorial-event-driven-jobs?source=recommendations)
with

- Azure Storage Queue
- Azure Service Bus Queue

![queue.png](docs/queue.png)

## Objectives

TODO: Overview Image

TODO: Define objective

- managed identity where possible
- serverless
- system & console logs

For example, a User Assigned Managed Identity (instead of access keys) is used to

- pull the image from the container registry
- process messages in a storage queue or service bus queue

## Content Overview

Source code for the docker images can be found in the [src directory](src).
Infrastructure is provisioned via Azure CLI commands in the [Makefile](Makefile).

- Execute a job & get the job execution status using REST API/Python
  SDK ([container_app_start_job.py](container_app_start_job.py))
- Create a Workbook to view system & console logs.

### Directory Structure

The structure is as follows:

```shell
.
├── docs
└── src
    ├── service_bus_queue
    │          └── src
    │               └── service_bus_queue
    ├── shared
    │        └── src
    │            └── shared
    └── storage_queue
        └── src
            └── storage_queue
```

### Storage Queue

- [Makefile](src%2Fstorage_queue%2FMakefile) to
    - build, run & push the docker container to an Azure Container Registry
    - write & process messages to/in storage queue
    - deploy container app job
    - delete container app job
- [Dockerfile](src%2Fstorage_queue%2FDockerfile) to process messages
    - Multistage Dockerfile for production and local development
    - Can be executed locally by mounting the azure credentials
- Example code to write messages to a **storage queue
  ** ([storage_queue_process.py](src%2Fstorage_queue%2Fsrc%2Fstorage_queue%2Fstorage_queue_process.py))
- Example code to process messages in a **storage queue
  ** ([storage_queue_write.py](src%2Fstorage_queue%2Fsrc%2Fstorage_queue%2Fstorage_queue_write.py))
    - messages are in JSON format
    - messages can be transformed into Pydantic models
    - messages are written to a poison queue if they can't be processed (checking the dequeue count)
    - messages that are received are not visible for a period of time, therefore can't be processed by other services

### Service Bus Queue

- [Makefile](src%2Fstorage_queue%2FMakefile) to
    - build, run & push the docker container to an Azure Container Registry
    - write & process messages to/in service bus queue
    - deploy container app job
    - delete container app job
- [Dockerfile](src%2Fservice_bus_queue%2FDockerfile) to process messages
    - Multistage Dockerfile for production and local development
    - Can be executed locally by mounting the azure credentials
- Example code to write messages to a **service bus queue
  ** ([service_bus_write.py](src%2Fservice_bus_queue%2Fsrc%2Fservice_bus_queue%2Fservice_bus_write.py))
- Example code to process messages in a **service bus queue
  ** ([service_bus_process.py](src%2Fservice_bus_queue%2Fsrc%2Fservice_bus_queue%2Fservice_bus_process.py))

## Provisioning Steps

Azure CLI commands are used to provision the resources on Azure.
You can find the commands in the [Makefile](Makefile).
Make sure to provide the variables in the "Variables" section at the top of the file.

### Resources

Here is a breakdown of resources that are provisioned & permissions that are granted.

- Resource Group
- Log Analytics Workspace
- User Assigned Managed Identity (UAMI)
- Container Registry
    - AcrPull permission (RBAC)
- Container Apps Environment
    - Diagnostics settings (console logs)
    - Diagnostics settings (system logs)
- Storage Account
    - Queue
    - Queue (Poison)
    - Storage Queue Data Contributor permission (RBAC)
- Service Bus Namespace
    - Queue
    - Service Bus Data Owner permission (RBAC)
- Workbook

After the resources have been created you can:

- create Container Apps Job(s) via the Makefile in one of the src directories
- [service_bus_queue](src%2Fservice_bus_queue)
- [storage_queue](src%2Fstorage_queue)
- send messages to or process messages in your queue
- see system & console logs in the workbook

### Permissions Notes:

- Assign UAMI Storage Queue Data Contributor (TODO: Storage Queue Data Message Processor should be
  enough? [Principle of Least Privilege](https://learn.microsoft.com/en-us/entra/identity-platform/secure-least-privileged-access))
- Assign UAMI Service Bus Data Owner (
  TODO: [Principle of Least Privilege](https://learn.microsoft.com/en-us/entra/identity-platform/secure-least-privileged-access),
  see [Rights required for Service Bus operations](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-sas#rights-required-for-service-bus-operations))

## Notes, Insights & TODOs

- When using an UAMI, don't forget to add AZURE_CLIENT_ID as environment variable in the container
- A [KEDA](https://keda.sh/) scaler evaluates scaling rules on a polling interval. A scaling rule for example would be
  checking an event source for messages (e.g. a queue). The scaling rule determines the number of replicas and runs them
  to meet demand.
  It is important to note that if you provision a functionally broken image that doesn't receive any messages (even
  though they exist), the scaling rule will execute a job for this message in every polling interval, creating an
  endless loop.
  Therefore, you should make sure that receiving messages is always possible. Additionally, you should make sure to use
  dead-lettering. Azure storage queue requires us to write the logic (application-level dead-lettering), e.g. add a
  poison queue, work with dequeue
  count and set the visibility parameter in the azure storage queue etc., while Azure service bus has system-provided
  dead-lettering.
- [Queues vs Topics](https://medium.com/@emer.kurbegovic/queues-vs-topics-a-simple-guide-with-real-world-examples-1d32947cb574):
    - **Queue**: single receiver ([FIFO](https://en.wikipedia.org/wiki/FIFO_(computing_and_electronics)))
      ![queue.png](docs/queue.png)
    - **Topic**: many receivers (No [FIFO](https://en.wikipedia.org/wiki/FIFO_(computing_and_electronics)))
      ![topic.png](docs/topic.png)
- ServiceBus Queue has system-provided dead-lettering & uses
  the [AMQP Protocol](https://d0znpp.medium.com/what-is-amqp-protocol-all-you-need-to-know-c9eedb680c71)
- Storage Queue has application-level dead-lettering
- The [KEDA scaler](https://keda.sh/docs/2.14/scalers/azure-service-bus/) for the Storage Queue requires the connection
  string of the Azure Storage Account
- The [KEDA scaler](https://keda.sh/docs/2.14/scalers/azure-storage-queue/) for the Service Bus Queue requires the
  connection string of the Azure Service Bus namespace

- [ ] Application Insights for Application Logs
- [ ] Monitoring Notebook (color based on log level)

## Resources

- https://learn.microsoft.com/en-us/azure/container-apps/jobs
- https://learn.microsoft.com/en-us/azure/container-apps/tutorial-event-driven-jobs
- https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/servicebus/azure-servicebus/samples
- https://www.nickthecloudguy.com/azure-event-driven-blobs-event-grid/
- https://techcommunity.microsoft.com/t5/apps-on-azure-blog/deploying-an-event-driven-job-with-azure-container-app-job-and/ba-p/3909279

### Scalers

- https://keda.sh/docs/2.14/scalers/azure-storage-queue/
- https://keda.sh/docs/2.14/scalers/azure-service-bus/

### Logging

- System Logs land in Log Analytics Workspace via settings in Container App Environment
- Console Logs land in Log Analytics Workspace via settings in Container App Environment
    - I recommend to use Application Insights (OpenTelemetry) for Console Logs

Default tables in Log Analytics Workspace

![img.png](img.png)

### Manged Identities

Currently, connection strings are required for the KEDA scaler (but this will change by the end of June 2024)

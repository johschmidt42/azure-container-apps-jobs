# Azure Container Apps Jobs

This repository explores the Azure Container Apps Jobs capabilities:

Scenario(s):

- [Queue based point-to-point communication with Azure Storage Queue/Azure Service Bus](https://learn.microsoft.com/en-us/azure/container-apps/tutorial-event-driven-jobs?source=recommendations)

## Objectives and Content Overview

TODO: Overview Image

- Dockerfile to create a service that processes messages ([Dockerfile](Dockerfile))
    - Multistage Dockerfile for production and development
    - Can be executed locally by mounting the azure credentials (see [Makefile](Makefile))
- Example code to write messages to a storage queue ([storage_queue_process.py](storage_queue_process.py))
- Example code to process messages in a storage queue ([storage_queue_write.py](storage_queue_write.py))
    - messages are in JSON format
    - messages can be transformed into pydantic models
    - messages are written to a poison queue
    - messages check the dequeue count
    - messages that are received are not visible for a period of time, therefore can't be processed by other services
- Example code to write messages to a service bus topic ([service_bus_write.py](service_bus_write.py))
- Example code to process messages in a service bus topic ([service_bus_process.py](service_bus_process.py))
- Execute a job & get the job execution status using REST API/Python SDK ([start_job.py](start_job.py))
- Show that a User Assigned Managed Identity (instead of access keys) is used to
    - pull the image from the container registry
    - process messages in a storage queue or service bus topic

## Provisioning Steps

### Resources

- Create User Assigned Managed Identity (UAMI)
- Create Container Registry
- Create Storage Account
    - Create Storage Queue
    - Create Storage Queue (Poison)
- Create Container Apps Environment
- Create Container Apps Jobs
    - Assign UAMI
    - Add secret ACR (TODO: replace with RBAC)
- Create a job

### Permissions:

- Assign UAMI ACR Pull permission
- Assign UAMI Storage Queue Data Contributor (TODO: Storage Queue Data Message Processor should be enough?)

## Notes, Insights & TODOs

- When using an UAMI, don't forget to add AZURE_CLIENT_ID as environment variable in the container
- A [KEDA](https://keda.sh/) scaler evaluates scaling rules on a polling interval. A scaling rule for example would be
  checking an event source for messages (e.g. a queue). The scaling rule determines the number of replicas and runs them
  to meet demand.
  It is important to note that if you provision a functionally broken image that doesn't receive any messages (even
  though they exist), the scaling rule will execute a job for this message in every polling interval, creating an
  endless loop.
  Therefore, you should make sure that receiving messages is always possible and add a poison queue, work with dequeue
  count and set the visibility parameter in the azure storage queue, so that longer running jobs not process the same
  message.

- [ ] Use UAMI to pull
  images (https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull?tabs=azure-cli&pivots=azure-portal)
- [ ] Try service bus

## Resources

- https://learn.microsoft.com/en-us/azure/container-apps/jobs?tabs=azure-portal
- https://www.nickthecloudguy.com/azure-event-driven-blobs-event-grid/

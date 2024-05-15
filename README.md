Steps

- Create User Assigned Managed Identity
- Create ACR
- Create Storage Account
    - Create Storage Queue
    - Create Storage Queue (Poison)
- Create Container Apps Environment
- Create Container Apps Jobs
    - Assign UAMI
    - Add secret ACR
    - Add secret Storage Account Connection String

Permissions:
- Assign UAMI ACR Pull permission
- Assign UAMI Storage Queue Data Contributor (Storage Queue Data Message Processor should be enough?)


Use Managed Identities where possible.

Image pull with managed identity:
https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull?tabs=azure-cli&pivots=azure-portal


#### TODO
- [X] Use UAMI to process messages -> Add AZURE_CLIENT_ID as environment variable
- [ ] Use UAMI to pull images
- [ ] Retry mechanisms
      -> dequeue_count
      -> visibility
      -> polling interval
- [ ] How to avoid endless executions
- [X] Use Azure CLI in Docker Image -> See [Makefile](Makefile)
- [ ] try min executions 2 but there is only 1 message
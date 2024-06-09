SHELL=/bin/bash

# Variables
subscription = a6feefeb-7f6b-425b-8311-b42ebeaee0d1
subscription_name = B-ID_Sandbox
resource_group = johannes-sandbox
location = westeurope

workspace_name = joh-log-analytics-workspace
user_assigned_managed_identity_name = joh-uami
container_registry = johcontainerregistry
container_apps_environment = joh-container-apps-environment

workbook_id = 445acf7a-8ddc-44d5-a07b-67bca9e9cc9f
workbook_name = joh-workbook
workbook_file = workbook.json

queue_name = messages

# Service Bus
service_bus_namespace = joh-service-bus-namespace

# Storage Account
storage_account_name = johstorageacc


#
# You can use tab for autocomplete on your terminal
# > make[space][tab]
#

.DEFAULT_GOAL := help
.PHONY: help
help:  ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

deploy-resource-group:  ## deploy azure resource group
	@az group create --subscription $(subscription) --name $(resource_group) --location $(location)

deploy-log-analytics-workspace: ## deploy azure log analytics workspace
	@az monitor log-analytics workspace create --subscription $(subscription) --resource-group $(resource_group) --workspace-name $(workspace_name) --location $(location)

deploy-uami:  ## deploy user assigned managed identity
	@az identity create --subscription $(subscription) --resource-group $(resource_group) --name $(user_assigned_managed_identity_name)

deploy-container-registry:  ## deploy azure container registry
	@az acr create --subscription $(subscription) --resource-group $(resource_group) --name $(container_registry) --sku Basic --admin-enabled false

deploy-container-app-environment:  ## deploy azure container apps environment
	@az containerapp env create --subscription $(subscription) --resource-group $(resource_group) --name $(container_apps_environment) --logs-destination azure-monitor --location $(location)

deploy-storage-account:  ## deploy storage account with queue & poison-queue
	@az storage account create --name $(storage_account_name) --subscription $(subscription) --resource-group $(resource_group) --location $(location) --sku "Standard_LRS" --kind "StorageV2" --access-tier "Hot"
	@az storage queue create --name $(queue_name) --account-name $(storage_account_name) --subscription $(subscription)
	@az storage queue create --name "$(queue_name)-poison" --account-name $(storage_account_name) --subscription $(subscription)

deploy-service-bus-namespace:  ## deploy service bus namespace with queue
	@az servicebus namespace create --name $(service_bus_namespace) --subscription $(subscription) --resource-group $(resource_group) --location $(location) --sku Standard
	@az servicebus queue create --name $(queue_name) --namespace-name $(service_bus_namespace) --subscription $(subscription) --resource-group $(resource_group)

##@ Monitoring

setup-diagnostic-settings-console-logs:  ## set up console logs for container apps environment
	@RESOURCE_ID=$$(az containerapp env show --subscription $(subscription) --resource-group $(resource_group) --name $(container_apps_environment) --query id --output tsv) && \
	az monitor diagnostic-settings create --subscription $(subscription) --resource-group $(resource_group) --name console-logs --resource $$RESOURCE_ID --workspace $(workspace_name) --logs '[{"category":"ContainerAppConsoleLogs","enabled":true}]'

setup-diagnostic-settings-system-logs:  ## set up system logs for container apps environment
	@RESOURCE_ID=$$(az containerapp env show --subscription $(subscription) --resource-group $(resource_group) --name $(container_apps_environment) --query id --output tsv) && \
	az monitor diagnostic-settings create --subscription $(subscription) --resource-group $(resource_group) --name system-logs --resource $$RESOURCE_ID --workspace $(workspace_name) --logs '[{"category":"ContainerAppSystemLogs","enabled":true}]'

deploy-workbook:  ## deploy azure monitor workbook to monitor jobs (convert workbook.json to string first)
	@SERIALIZED_CONTENT=$$(cat $(workbook_file) | jq -c | jq -R) && \
	az monitor app-insights workbook create --subscription $(subscription) --name $(workbook_id) --resource-group $(resource_group) --display-name $(workbook_name) --serialized-data "$$SERIALIZED_CONTENT" --location $(location) --kind "shared" --source-id "azure monitor"

## Permissions

assign-acr-pull:
	@RESOURCE_ID_ACR=$$(az acr show --name $(container_registry) --subscription $(subscription) --resource-group $(resource_group) --query id --output tsv) && \
	CLIENT_ID_UAMI=$$(az identity show --name $(user_assigned_managed_identity_name) --subscription $(subscription) --resource-group $(resource_group) --query clientId --output tsv) && \
	az role assignment create --assignee $$CLIENT_ID_UAMI --role AcrPull --scope $$RESOURCE_ID_ACR

assign-storage-queue-data-contributor:
	@RESOURCE_ID=$$(az storage account show --name $(storage_account_name) --subscription $(subscription) --resource-group $(resource_group) --query id --output tsv) && \
	CLIENT_ID_UAMI=$$(az identity show --name $(user_assigned_managed_identity_name) --subscription $(subscription) --resource-group $(resource_group) --query clientId --output tsv) && \
	az role assignment create --assignee $$CLIENT_ID_UAMI --role "Storage Queue Data Contributor" --scope $$RESOURCE_ID

assign-service-bus-data-owner:
	@RESOURCE_ID=$$(az servicebus namespace show --name $(service_bus_namespace) --subscription $(subscription) --resource-group $(resource_group) --query id --output tsv) && \
	CLIENT_ID_UAMI=$$(az identity show --name $(user_assigned_managed_identity_name) --subscription $(subscription) --resource-group $(resource_group) --query clientId --output tsv) && \
	az role assignment create --assignee $$CLIENT_ID_UAMI --role "Azure Service Bus Data Owner" --scope $$RESOURCE_ID

##@ Stuff

get-id-container-apps-environment:
	@az containerapp env show --subscription $(subscription) --resource-group $(resource_group) --name $(container_apps_environment) --query id --output tsv

list-categories:
	@RESOURCE_ID=$$(az containerapp env show --subscription $(subscription) --resource-group $(resource_group) --name $(container_apps_environment) --query id --output tsv) && \
	az monitor diagnostic-settings categories list --resource $$RESOURCE_ID

get-id-container-registry:
	@az acr show --name $(container_registry) --subscription $(subscription) --resource-group $(resource_group) --query id --output tsv

get-id-uami:
	@az identity show --name $(user_assigned_managed_identity_name) --subscription $(subscription) --resource-group $(resource_group) --query id --output tsv

get-client-id-uami:
	@az identity show --name $(user_assigned_managed_identity_name) --subscription $(subscription) --resource-group $(resource_group) --query clientId --output tsv

set-subscription:
	@az account set --subscription $(subscription)

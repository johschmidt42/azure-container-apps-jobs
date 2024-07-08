SHELL=/bin/bash

# Variables
subscription = a6feefeb-7f6b-425b-8311-b42ebeaee0d1
subscription_name = B-ID_Sandbox
resource_group = johannes-sandbox
location = westeurope

package_name = storage_queue
container_registry = johcontainerregistry
image_name = johcontainerregistry.azurecr.io/container-apps-jobs
image_tag = storage-queue

container_app_job_name = joh-aca-job-storage-queue
container_apps_environment = joh-container-apps-environment
storage_account_name = johstorageacc
queue_name = messages
user_assigned_managed_identity_name = joh-uami

#
# You can use tab for autocomplete on your terminal
# > make[space][tab]
#

.DEFAULT_GOAL := help
.PHONY: help
help:  ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

format:  ## format code using ruff
	@ruff format .
	@ruff check --fix-only .

lint:  ## run linter using ruff
	@ruff check .

build-release:  ## build docker image (release)
	@cd ../; docker build --file ./$(package_name)/Dockerfile --target release --platform linux/amd64 --tag $(image_name):$(image_tag) .

build-dev:  ## build docker image (dev)
	@cd ../; docker build --file ./$(package_name)/Dockerfile --target dev --platform linux/amd64 --tag $(image_name):$(image_tag) .

run:  ## run docker image (dev) with mounted azure credentials
	@docker run --platform linux/amd64 -it --rm -v ~/.azure:/root/.azure $(image_name):$(image_tag)

run-bash:  ## run docker image (dev) with bash
	@docker run --platform linux/amd64 -it --rm -v ~/.azure:/root/.azure $(image_name):$(image_tag) /bin/bash

push:  ## push docker image to container registry
	@az acr login --name $(container_registry)
	@docker push $(image_name):$(image_tag)

write-message-queue:  ## writes a message to the queue
	@PYTHONPATH="../shared/src" python src/$(package_name)/storage_queue_write.py

process-message-queue: ## process a message from the queue
	@PYTHONPATH="../shared/src" python src/$(package_name)/storage_queue_process.py

##@ Deploy

set-subscription:  # set the subscription in your AZ CLI
	@az account set --subscription $(subscription)

deploy-container-job:  # deploys a container apps job (requires existing image)
	@QUEUE_CONNECTION_STRING=$$(az storage account show-connection-string -g $(resource_group) --name $(storage_account_name) --query connectionString --output tsv) && \
	RESOURCE_ID=$$(az identity show --name $(user_assigned_managed_identity_name) --subscription $(subscription) --resource-group $(resource_group) --query id --output tsv) && \
	CLIENT_ID_UAMI=$$(az identity show --name $(user_assigned_managed_identity_name) --subscription $(subscription) --resource-group $(resource_group) --query clientId --output tsv) && \
	az containerapp job create \
    --name "$(container_app_job_name)" \
    --subscription "$(subscription)" \
    --resource-group "$(resource_group)" \
    --environment "$(container_apps_environment)" \
    --trigger-type "Event" \
    --replica-timeout "1800" \
    --min-executions "0" \
    --max-executions "1" \
    --polling-interval "60" \
    --scale-rule-name "$(image_tag)" \
    --scale-rule-type "azure-queue" \
    --scale-rule-metadata "accountName=$(storage_account_name)" "queueName=$(queue_name)" "queueLength=1" \
    --scale-rule-auth "connection=connection-string-secret" \
    --image "$(image_name):$(image_tag)" \
    --cpu "0.5" \
    --memory "1Gi" \
    --secrets "connection-string-secret=$$QUEUE_CONNECTION_STRING" \
    --env-vars "AZURE_STORAGE_QUEUE_NAME=$(queue_name)" "AZURE_STORAGE_CONNECTION_STRING=secretref:connection-string-secret" "AZURE_CLIENT_ID=$$CLIENT_ID_UAMI" \
    --mi-user-assigned "$$RESOURCE_ID" \
    --registry-identity "$$RESOURCE_ID" \
    --registry-server "$(container_registry).azurecr.io"

delete-container-job:
	@az containerapp job delete --name "$(image_tag)" --subscription "$(subscription)" --resource-group "$(resource_group)" --yes
